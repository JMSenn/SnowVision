//used to filter project from site and then context from project and site in javascript
//This allows users to only choose valid assocations of site, project, and context when
//creating new sherds and contexts
function filterproject(fsite) {

  // store this name of the site
  console.log(fsite);
  var site = fsite.find('option:selected').val();
  console.log(site);
  $.ajax({
    url: '/snowvision/filter/project',
    data: {
      'site': site,
    },
    dataType: 'json',
    success: function (data) {
      //Remove all previous project options
      $('#id_project option:gt(0)').remove();


      for (var i=0; i<data.length; i++){
        $('#id_project')
          .append( $("<option></option>")
          .attr("value",data[i]["id"])
          .text(data[i]["name"]) );
      } // for (var i=0; i<data.length; i++){
    } // success
  }) //$.ajax({

  // Enable project selection
  $('#id_project').attr('disabled', false);
  $('#id_context').attr('disabled', true);
  $('#id_context option:gt(0)').remove();

}; // $('#id_site').change(function () {



function filtercontext(fproject) {

  var site = $('#id_site').find('option:selected').attr("value");
  var project = fproject.find('option:selected').attr("value");

  console.log("site: " + site)
  console.log("project: " + project)


  $.ajax({
    url: '/snowvision/filter/context',
    data: {
      "site": site,
      "project": project,
    },
    success: function (data) {
      // Remove all previous contexts
      $('#id_context option:gt(0)').remove();
      console.log(data);

      for (var i=0; i<data.length; i++) {
        $('#id_context')
          .append( $("<option></option>")
          .attr("value", data[i]["id"])
          .text(data[i]["full_name"]));
      } //  for (var i=0; i<data.lenth; i++) {
    } // success: function (data) {
  }); //$.ajax({

  // Enable context selection
  $('#id_context').attr('disabled', false);

 }; //   $('#id_project').change(function () {
