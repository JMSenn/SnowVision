#PLEASE READ BEFORE RUNNING!
#This script will populate certain relatively constant tables within the sherd
#database with values. This script was written during development so that
#when the database was dropped this could be run and re-populate the database quickly
#THIS SHOULD NOT BE RUN POST-DEVELOPMENT WHEN THE DATABASE IS PAST PRODUCTION PHASE

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SnowVision.settings')

import django
django.setup()

from SnowVisionApp.models import *

#types of symmetry that a sherd can possess
symmetry_list = [
    'unknown/indeterminate',
    'asymmetrical',
    'double-axis',
    'single-axis',
    'court-card'
    ]

#eco region three list with eco region four sublist to populate eco region tables
eco_region_dict = {
    'Blue Ridge':[
        'Broad Basins',
        'Southern Crystalline Ridges and Mountains',
        'Southern Metasedimentary Mountains',
        ],
    'Interior Plateau':[
        'Eastern Higland Rim',
        'Little Mountain',
        'Outer Nashville Basin',
        'Western Highland Rim',
    ],
    'Middle Atlantic Coastal Plain':[
         'Carolina Flatwoods',
         'Carolinian Barrier Islands and Coastal Marshes',
         'Mid-Atlantic Floodplains and Low Terraces',

    ],
    'Piedmont':[
        'Carolina Slate Belt',
        'Kings Mountain',
        'Pine Mountain Ridges',
        'Southern Inner Piedmont',
        'Southern Outer Piedmont',
        'Talladega Upland',
        'Triassic Basins',
    ],
    'Ridge and Valley':[
        'Southern Dissected Ridges and Knobs',
        'Southern Limestone/Dolomite Valleys and Low Rolling Hills',
        'Southern Sandstone Ridges',
        'Southern Shale Valleys',
    ],

    'Southeasten Plains':[
        'Atlantic Southern Loam Plains',
        'Blackland Prairie',
        'Buhrstone/Lime Hills',
        'Coastal Plain Red Uplands',
        'Dougherty Plain',
        'Fall Line Hills',
        'Flatwoods/Blackland Prairie Margins',
        'Sand Hills',
        'Southeastern Floodplains and Low Terraces',
        'Southern Hilly Gulf Coastal Plain',
        'Southern Pine Plains and Hills',
        'Tallahasee Hills/Valdosta Limesink',
        'Tifton Upland',
        'Transition Hills',

    ],
    'Southern Coastal Plains':[
        'Bacon Terraces',
        'Floodplains and Low Terraces',
        'Gulf Barrier Islands and Coastal Marshes',
        'Gulf Coast Flatwoods',
        'Okefenokee Plains',
        'Okefenokee Swamp',
        'Sea Island Flatwoods',
        'Sea Islands/Coastal Marsh',
    ],

    'Southeastern Appalachians':[
        'Cumberland Plateau',
        'Dissected Plateau',
        'Plateau Escarpment',
        'Sequatchie Valley',
        'Shale Hills',
        'Southern Table Plateaus',
    ]
    }


journal_list = [
    'American Antiquity',
    'Early Georgia',
    'Journal of Alabama Archaeology',
    'Journal of Archaeological Science',
    'South Carolina Antiquities',
    'Southeastern Archaeology'
    ]

recovery_method_list = [
    'Unknown',
    'Surface Find',
    'Test Unit',
    'Feature'
    ]

screen_type_list = [
    'Unknown',
    'Not Applicable (e.g., Surface Find,)',
    '1/2 inch',
    '1/4 inch',
    '1/8 inch',
    '1/16 inch (e.g., Flotation)'
    ]

curated_by_list = [
    'University of Georgia, Athens, GA',
    'Georgia Southern University, Statesboro, GA',
    'Antonio J. Warning, Jr. Archaeological Laboratory',
    'State University of West Georgia, Carrollton, GA',
    'Southeastern Archaeological Center, Tallahassee, FL',
    'University of Florida, Gainesville, FL',
    'Florida State University, Tallahassee, FL',
    'University of West Florida, Pensacola, FL',
    'South Carolina Institute of Archaeology and Anthropology',
    'Office of Archaeological Research, Moundville, AL'
    ]

site_list={
    'Candy Creek',
    'Danville',
    'Fairchilds Landing',
    'Kolomoki',
    'Mandeville',
    'Milamo',
    'Quartermaster',
    'Swift Creek',
    'Uchee',
    'Wakulla County'
}

page_list = {
    'Home',
    'About',
}

def initial_population():
        #populate symmetry types
    for option in symmetry_list:
            new_sym = Symmetry.objects.get_or_create(name = option)[0]
            new_sym.save()

    for region in eco_region_dict:
        new_reg = EcoRegionThree.objects.get_or_create(region_type = region)[0]
        new_reg.save()

        for subregion in eco_region_dict[region]:
            new_reg_four = EcoRegionFour.objects.get_or_create(eco_region_three = new_reg, region_type = subregion)[0]
            new_reg_four.save()

    for option in journal_list:
        new_journ = Journal.objects.get_or_create(name = option)[0]
        new_journ.save()

    for option in recovery_method_list:
        new_recovmeth = RecoveryMethod.objects.get_or_create(name = option)[0]
        new_recovmeth.save()

    for option in screen_type_list:
        new_scrn = ScreenType.objects.get_or_create(name = option)[0]
        new_scrn.save()

    for option in curated_by_list:
        new_cur = Curator.objects.get_or_create(name = option)[0]
        new_cur.save()


if __name__ == '__main__':
    print("Populating the databases...Please Wait")
    initial_population()
    print('Populating Complete')
