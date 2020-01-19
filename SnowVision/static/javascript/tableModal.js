//used on an image to set as a modal images
//https://www.w3schools.com/howto/howto_css_modal_images.asp
$('#tableModal').modal({
  keyboard: true,
  backdrop: "static",
  show: false,
}).on('shown.bs.modal', function(event){
  var trow = $(event.relatedTarget).closest('a');
  $(this).find('#designID').text(trow.attr('id'))
  $(this).find('#modalImage').html(trow.html());
});

// Removes modal on hide
$('#tableModal').on('hidden.bs.modal', function() {
  $(this).find('#designID').text("")
  $(this).find('#modalImage').html("");
});


// Modal Class
// <div class="modal fade" id="tableModal" role="dialog">
//     <div class="modal-dialog">
//         <div class = "modal-content">
//             <div class="modal-header">
//                 <a class="close" data-dismiss="modal">×</a>
//                 <h3 id="designID"></h3>
//             </div>
//             <div id="modalImage" class="modal-body"></div>
//             <div class="modal-footer">
//               <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
//             </div>
//         </div>
//     </div>
// </div>
