from django.template import Context, RequestContext
from django.template.loader import render_to_string

from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.http import HttpRequest, JsonResponse, HttpResponse, Http404
from django.forms.models import model_to_dict
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.urls import reverse, reverse_lazy
from django.core.mail import EmailMessage

from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.views.generic import (View, TemplateView, CreateView, DeleteView, UpdateView, DetailView)

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.decorators import method_decorator

import zipfile, zlib
import io
import os
from itertools import chain
import threading
import csv
import json
import datetime

from SnowVisionApp import models, forms, tasks, blackbox, tokens


# Create your views here.

# returns a csv of sherd or design data when requested by sherd query or design query page
def get_csv(request):
    # TODO: Error check on dictionary. Hackers can change javascript
    if request.method == "POST":
        response = HttpResponse(content_type='text/csv')
        filename = request.POST.get('object_type') + "_query_" + datetime.datetime.now().strftime("%Y-%m-%d") + ".csv"
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        writer = csv.writer(response)
        pks = request.POST.getlist('pk')

        if request.POST.get('object_type') == 'sherd':
            sherds = models.Sherd.objects.filter(pk__in=pks)
            writer.writerow(['#','Overstamped','Design', 'Context','Context Recovery Method','Context Screen Type','Context Curator','Site','Project','Uploader'])
            for sherd in sherds:
                writer.writerow([
                    str(sherd.pk),
                    str(sherd.overstamped),
                    str(sherd.design),
                    sherd.context.name,
                    sherd.context.recovery_method.name,
                    sherd.context.screen_type.name,
                    sherd.context.curator.name,
                    sherd.context.site.name,
                    sherd.context.project.name,

                    str(sherd.profile),
                ])


        elif request.POST.get('object_type') == 'design':
            designs = models.Design.objects.filter(pk__in=pks)
            writer.writerow(['Design', 'Artist', 'Design Elements', 'Symmetry', 'Line Filler', 'Framing', 'Complete'])
            for design in designs:
                elements=""
                for element in design.elements.all():
                    elements += element.name + " "
                writer.writerow([
                    str(design.number),
                    design.artist,
                    elements,
                    design.symmetry.name,
                    str(design.line_filler),
                    design.framing,
                    str(design.completeness),
                ])

    return response

# returns a zipfile of images when requested by sherd query or design query page
def get_images(request):
  
    if request.method == "POST":
        pks = request.POST.getlist('pk')
        if request.POST.get('object_type') == 'sherd':
            sherds = models.Sherd.objects.filter(pk__in=pks)
            zip_subdir = "sherd_query_images"
            zip_filename = "%s.zip" % zip_subdir
            s = io.BytesIO()
            zf = zipfile.ZipFile(s, "w", zipfile.ZIP_DEFLATED )

            file_paths = []
            file_names = {"key":"value"}
            for sherd in sherds:
                if os.path.isfile(settings.MEDIA_ROOT + sherd.rgb_image.name):
                    file_path = str(settings.MEDIA_ROOT + sherd.rgb_image.name)
                    file_paths.append(file_path)
                    file_names[file_path] = {"Sherd_"+str(sherd.pk)+","+sherd.context.name+","+sherd.context.site.name+","+sherd.context.project.name}

            for fpath in file_paths:
                # Calculate path for file in zip
                fdir, fname = os.path.split(fpath)
                zip_path =str(file_names[fpath])+".png"

                # Add file, at correct path
                zf.write(fpath, zip_path)

            zf.close()

            # Grab ZIP file from in-memory, make response with correct MIME-type
            response = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
            # ..and correct content-disposition
            response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

            return response

        elif request.POST.get('object_type') == 'design':
            designs = models.Design.objects.filter(pk__in=pks)
            zip_subdir = "design_query_images"
            zip_filename = "%s.zip" % zip_subdir
            s = io.BytesIO()
            zf = zipfile.ZipFile(s, "w", zipfile.ZIP_DEFLATED )

            file_paths = []
            for design in designs:
                if os.path.isfile(settings.MEDIA_ROOT + design.greyscale_image.name):
                    file_path = str(settings.MEDIA_ROOT + design.greyscale_image.name)
                    file_paths.append(file_path)

            for fpath in file_paths:
                # Calculate path for file in zip
                fdir, fname = os.path.split(fpath)
                zip_path = os.path.join(zip_subdir, fname)

                # Add file, at correct path
                zf.write(fpath, zip_path)

            zf.close()

        # Grab ZIP file from in-memory, make response with correct MIME-type
        response = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
        # ..and correct content-disposition
        response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename


        return response


class NoPageView(TemplateView):
    template_name = 'SnowVisionApp/no_page.html'

# About the Project
class AboutView(TemplateView):
    template_name = 'SnowVisionApp/about.html'

# details about algorithm
class AlgorithmView(TemplateView):
    template_name = 'SnowVisionApp/about_snowvision.html'

# research conducted by world engraved members
class ResearchView(TemplateView):
    template_name = 'SnowVisionApp/research.html'

# home page
class IndexView(TemplateView):
    template_name = 'SnowVisionApp/index.html'

# users signs up for a profile
def signup(request):
    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.save()
            current_site = get_current_site(request)

            #send user registration email with activation link
            message = render_to_string('registration/acc_active_email.html', {
                'user':user,
                'domain':current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': tokens.account_activation_token.make_token(user),
            })
            mail_subject = 'Activate your blog account.'
            to_email = form.cleaned_data.get('email')
            subject = "Snow Vision Account Activation"
            email = EmailMessage(subject, message, to=[to_email])
            email.send()
            return render(request, 'registration/confirm.html')
    else:
        form = forms.SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# activation request from user
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and tokens.account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('index')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

# user profile information view
# contexts, sherds, collections, profile info
def user_profile(request):
    user_sherds = None
    template_name = 'SnowVisionApp/user_profile.html'
    if request.user.is_authenticated():
        user_sherds = models.Sherd.objects.filter(profile__user = request.user)
        user_contexts = models.Context.objects.filter(profile__user = request.user)
        user_collections = models.Sherd_Collection.objects.filter(profile__user = request.user)
        context = {
            'user_sherds':user_sherds,
            'user_contexts':user_contexts,
            'user_collections':user_collections,
        }
    else:
        context = None
    return render(request,template_name,context)


# used by json to filter project based on site selection on sherd form
def filter_project(request):
    
    if request.method == "GET":
        site = request.GET.get('site', 0)
        projects =  models.Project.objects.filter(site__pk=int(site))

        data = []
        for i in projects:
            data.append( dict(model_to_dict(i, fields=["id", "name", "excavator"])) )

        return JsonResponse(data, safe=False)

# used by json to filter context based on site and project selection on sherd page
def filter_context(request):
    if request.method == "GET":
        site = request.GET.get('site', "")
        project = request.GET.get('project', "")
       
        contexts = models.Context.objects.all()
        if len(site)!=0:
            contexts = models.Context.objects.filter(site__pk=int(site))
        if len(project)!=0:
            contexts = contexts.filter(project__pk=int(project))

        data = [{"id": context.id, 'full_name': context.full_str()} for context in contexts]

        return JsonResponse(data, safe=False)


def filter_collection(request):
    if request.method == "GET":
        profile = request.user.profile
        profile_collections =  models.Sherd_Collection.objects.filter(profile__pk=profile.pk)

        data = []
        for i in profile_collections:
            data.append( dict(model_to_dict(i, fields=["id", "name"])) )

        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({"wata": "nutta"})

# view used to create a sherd
def create_sherd_view(request):
    if request.method == 'POST':
        sherd_form = forms.SherdCreateForm(request.POST, request.FILES)
        if sherd_form.is_valid():
            sherd = sherd_form.save()
            user = request.user
            if (user.is_authenticated()):
                user.refresh_from_db()
                sherd.profile = user.profile
            sherd.save()
            current_site = get_current_site(request).domain

            if settings.DEBUG:
                t = threading.Thread(target=blackbox.match, kwargs={'sherd_pk':sherd.pk, 'current_site':current_site} )
                t.setDaemon(True)
                t.start()

            else:
                celery_job = tasks.match_to_design.delay(sherd.pk, current_site)

            #if a user wants to save fields for next submit
            if request.POST.get("save"):
                old_form = sherd_form
                sherd_form = forms.SherdCreateForm(initial={
                    # 'overstamped':old_form.cleaned_data['overstamped'][0],
                })
                #if users indicates they want to submit a similar
                #sherd the data is save and return as a context
                #dict to sherd_form page
                old_site = request.POST.get("site")
                old_project = request.POST.get("project")
                old_context =request.POST.get("context")
                old_design =request.POST.get("design")

                context = {
                    'old_site':old_site,
                    'old_project':old_project,
                    'old_context':old_context,
                    'old_design':old_design,
                    'old_data': 1,
                    'form' : sherd_form,
                    'site_list': models.Site.objects.all(),
                    'project_list': models.Project.objects.all(),
                    'recovery_method_list': models.RecoveryMethod.objects.all(),
                }
                return render(request,'SnowVisionApp/sherd_form.html', context)
            else:
                return redirect(sherd)

        else:
            context = {
                'old_data': 0,
                'form' : sherd_form,
                'site_list': models.Site.objects.all(),
                'project_list': models.Project.objects.all(),
                'recovery_method_list': models.RecoveryMethod.objects.all(),
            }
            return render(request,'SnowVisionApp/sherd_form.html', context)

    else:
        sherd_form = forms.SherdCreateForm()

    context = {
        'old_data': 0,
        'form' : forms.SherdCreateForm(),
        'site_list': models.Site.objects.all(),
        'project_list': models.Project.objects.all(),
        'recovery_method_list': models.RecoveryMethod.objects.all(),
    }

    return render(request, 'SnowVisionApp/sherd_form.html', context)


class SherdUpdateView(UpdateView):
    model = models.Sherd
    form_class = forms.SherdUpdateForm
    template_name = "SnowVisionApp/sherd_form.html"


# used to delete a sherd that the profile owns
class SherdDeleteView(DeleteView):
    model = models.Sherd
    template_name = "SnowVisionApp/user_profile.html"
    success_url = reverse_lazy('user_profile')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        sherd = super(SherdDeleteView, self).get_object()
        if not sherd.profile.user == self.request.user:
            raise Http404
        return sherd

# used to create a context for authorized user
def create_context_view(request):
    if request.method == 'POST':
        context_form = forms.ContextCreateForm(request.POST, request.FILES)
        if context_form.is_valid():
            context = context_form.save()
            user = request.user
            if (user.is_authenticated()):
                user.refresh_from_db()
                context.profile = user.profile
            context.save()
            return redirect(context)

        else:
            context_form = forms.ContextCreateForm
            context = {
                'form' : context_form,
            }
            return render(request,'SnowVisionApp/context_form.html', context)

    else:
        context_form = forms.ContextCreateForm()

        
    context = {
        'form' : forms.ContextCreateForm(),
    }

    return render(request, 'SnowVisionApp/context_form.html', context)


# updates context on selected fields
class ContextUpdateView(UpdateView):
    template_name = "SnowVisionApp/context_form.html"
    form_class = forms.ContextUpdateForm
    model = models.Context

# used to query and filter through sherds to returns a list of sherds
def sherd_search(request):
    template_name = 'SnowVisionApp/sherd_query.html'
    #returns lists of objects for selection on query page
    site_list = models.Site.objects.all()
    project_list = models.Project.objects.all()
    context_list = models.Context.objects.all()
    recovery_method_list = models.RecoveryMethod.objects.all()
    eco_region_four_list = models.EcoRegionFour.objects.all()
    eco_region_three_list = models.EcoRegionThree.objects.all()
    design_list = models.Design.objects.all()
    

    sherd_list = None
    if(request.GET):

        query_dict = request.GET
        sherd_list = models.Sherd.objects.all()

        if query_dict.__contains__('site'):
            sherd_list = sherd_list.filter(context__site__pk__in=query_dict.getlist('site'))

        if query_dict.__contains__('project'):
            sherd_list = sherd_list.filter(context__project__pk__in=query_dict.getlist('project'))

        if query_dict.__contains__('context'):
            sherd_list = sherd_list.filter(context__pk__in=query_dict.getlist('context'))

        if query_dict.__contains__('eco_region_three'):
            sherd_list = sherd_list.filter(
                context__site__eco_region_four__eco_region_three__pk__in=query_dict.getlist('eco_region_three'))

        if query_dict.__contains__('eco_region_four'):
            sherd_list = sherd_list.filter(
                context__site__eco_region_four__pk__in=query_dict.getlist('eco_region_three'))

        if query_dict.__contains__('design'):
            sherd_list =sherd_list.filter(design__pk__in= query_dict.getlist('design'))

        if query_dict.__contains__('recovery_method'):
                sherd_list = sherd_list.filter(context__recovery_method__pk__in=query_dict.getlist('recovery_method'))

    context = {
        'site_list': site_list,
        'project_list': project_list,
        'context_list': context_list,
        'recovery_method_list': recovery_method_list,
        'eco_region_four_list': eco_region_four_list,
        'eco_region_three_list': eco_region_three_list,
        'design_list': design_list,
        'sherd_list': sherd_list
    }
      
    return render(request, template_name, context)

# displays all sites within database on map
def sherd_map(request):
    template_name = "SnowVisionApp/sherd_map.html"
    site_list = list(models.Site.objects.all())
    context={'site_list': site_list}

    return render(request, template_name, context)

# filter through designs based on fields the user has selected
# returns list of designs
def design_search(request):
    template_name = 'SnowVisionApp/design_query.html'
    print("\n\n", request.GET, "\n\n")

    design_complete_list = models.Design.objects.all()
    site_list = models.Site.objects.all()
    project_list = models.Project.objects.all()
    recovery_method_list = models.RecoveryMethod.objects.all()
    design_element_list = models.DesignElement.objects.all()

    design_list = models.Design.objects.none()

    sherd_list = models.Sherd.objects.none()
    if(request.GET):
        query_dict = request.GET
        design_list = models.Design.objects.all()


        #filtering through to grab correct designs matching query_dict
        #filter by design number
        if query_dict.__contains__('number'):
            #fi
            number_design_list = models.Design.objects.filter(number__in=query_dict.getlist('number'))

            design_list = (number_design_list & design_list)

        #add designs sharing this site to total designs
        site_design_list = models.Design.objects.none()
        if query_dict.__contains__('site'):
            sherd_list = models.Sherd.objects.filter(context__site__pk__in=query_dict.getlist('site'))
            for sherd in sherd_list:
                design_object = models.Design.objects.filter(pk =sherd.design.pk)
                site_design_list = (site_design_list | design_object)

            design_list = (site_design_list & design_list)

        #add designs sharing this project to total designs
        project_design_list = models.Design.objects.none()
        if query_dict.__contains__('project'):
            project_sherd_list = models.Sherd.objects.filter(context__project__pk__in=query_dict.getlist('project'))
            for sherd in project_sherd_list:
                design_object = models.Design.objects.filter(pk =sherd.design.pk)
                project_design_list= (project_design_list | design_object)

            design_list = ( project_design_list & design_list)

        #keep only designs with line_filler True or False based on user input
        if query_dict.__contains__('line_filler'):
            if query_dict.get('line_filler') == 'True':
                design_list = design_list.filter(line_filler =True)
            elif query_dict.get('line_filler') == 'False':
                design_list = design_list.filter(line_filler =False)

        #keep only designs with completeness True or False based on user input
        if query_dict.__contains__('completeness'):
            if query_dict.get('completeness') == 'True':
                design_list = design_list.filter(completeness =True)
            elif query_dict.get('completeness') == 'False':
                design_list = design_list.filter(completeness =False)

        #keep only designs containing selected elements
        if query_dict.__contains__('elements'):
            for element_pk in query_dict.getlist('elements'):
                design_list =design_list.filter(elements__pk = element_pk)

    sherds_with_designs = models.Sherd.objects.filter(design__in =design_list)


    context = {
                'design_complete_list':design_complete_list,
                'site_list':site_list,
                'project_list':project_list,
                'design_list':design_list,
                'design_element_list':design_element_list,
                'sherds_with_designs':sherds_with_designs,

                }

    return render(request,template_name, context)


# display more detailed information about site
class SiteDetailView(DetailView):
    # fields =('site_number','eco_region_four','name','state_and_county',)
    context_object_name = 'site_detail'
    template_name = "SnowVisionApp/site_detail.html"
    model = models.Site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        designs = models.Design.objects.none()
        sherds = models.Sherd.objects.filter(context__site__pk__iexact=self.kwargs['pk'])

        for sherd in sherds:
            design_object = models.Design.objects.filter(pk = sherd.design.pk)
            designs = (designs | design_object)

        context['designs'] = designs.distinct()
        return context

#display more detailed information about sherd
class SherdDetailView(DetailView):
    # fields =('context','overstamped','rgb_image','design',)
    context_object_name = 'sherd_detail'
    template_name = "SnowVisionApp/sherd_detail.html"
    model = models.Sherd

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        matched_designs = models.MatchPercentage.objects.filter(sherd__pk__iexact=self.kwargs['pk'])
        context['matched_designs'] = matched_designs

        return context

#display more detailed information about a give design
class DesignDetailView(DetailView):
    fields = ('number', 'design_reference', 'elements',
                'symmetry', 'line_filler','completeness', 'framing',
                'artist','curve_image', 'greyscale_image',
                )
    context_object_name = 'design_detail'
    template_name = "SnowVisionApp/design_detail.html"
    model = models.Design

#credits page
class CreditsView(TemplateView):
    template_name = "SnowVisionApp/credits.html"

class CollectionDetailView(DetailView):
    fields = "__all__"
    model = models.Sherd_Collection
    template_nname = "SnowVisionApp/sherd_collection_detail.html"
    context_object_name = "collection_detail"

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        collection_sherds = models.Sherd.objects.filter(collection__pk = self.kwargs['pk'])

        context['collection_sherds']=collection_sherds
        return context

class CollectionDeleteView(DeleteView):
    model = models.Sherd_Collection
    template_name = "SnowVisionApp/user_profile.html"
    success_url = reverse_lazy('user_profile')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        collection = super(CollectionDeleteView, self).get_object()
        if not collection.profile.user == self.request.user:
            raise Http404
        sherds_in_collection = models.Sherd.objects.filter(profile__pk = self.request.user.profile.pk)
        if(sherds_in_collection == models.Sherd.objects.none()):
            raise Http404

        return collection

def create_collection_view(request):
    template_name = "SnowVisionApp/user_profile.html"
    if request.method == 'POST':
        new_collection_name = request.POST.get("create_collection")
        new_collection = models.Sherd_Collection.objects.create(
            name = new_collection_name,
            profile = request.user.profile,
        )
        new_collection.save()

    context ={}
    return redirect(new_collection)

