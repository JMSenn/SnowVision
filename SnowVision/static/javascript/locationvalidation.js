//grabs an address and validates it use the google geocoder
$("#btn").click(function(){
            var geocoder =  new google.maps.Geocoder();
    geocoder.geocode( { 'address': 'docs, us'}, function(results, status) {
          if (status == google.maps.GeocoderStatus.OK) {
          } else {
            alert("Invalid Location" + status);
          }
        });
});
