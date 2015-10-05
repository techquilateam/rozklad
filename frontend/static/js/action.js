function myOwnSort(oldIndex, newIndex, oldTable, draggedItem){
	if (newIndex != 0) {
		$(draggedItem).prev().clone().insertAfter($(oldTable).find('li').eq(oldIndex - 1))
		$(oldTable).find('li').eq(oldIndex).css('opacity', 0).css('height', 0).css('display', 'block').animate({opacity: 1, height: 70}, 450)
		$(draggedItem).prev().animate({opacity: 0, height: 0}, 450, function() {$(this).remove()})
	} else {
		$(draggedItem).next().clone().insertAfter($(oldTable).find('li').eq(oldIndex - 1))
		$(oldTable).find('li').eq(oldIndex).css('opacity', 0).css('height', 0).css('display', 'block').animate({opacity: 1, height: 70}, 450)
		$(draggedItem).next().animate({opacity: 0, height: 0}, 450, function() {$(this).remove()})
	}
}
function hoverElement(relatedItem, draggedItem){
	$(relatedItem).animate({opacity: 0.5, height: 50}, 400)
	$(relatedItem).find('i').animate({opacity: 0}, 400)
}
function clearize(){
	$('.moveAble').animate({opacity: 1, height: 70}, 400)
	$('.moveAble').find('i').animate({opacity: 0.2}, 400)
}
for (i = 1; i < 7; i++) 
	Sortable.create(document.getElementById("w-1_list-" + i),{group: "timetable",sort: true,forceFallback: true,animation: 400,handle: '.handle',
		onAdd: function (evt) {
			myOwnSort(evt.oldIndex,evt.newIndex, evt.from, evt.item)
			clearize()
	    },
	    onMove: function (evt) {
			clearize()
	        hoverElement(evt.related, evt.dragged)
	    },
	    onUpdate: function (evt) {
			clearize()
	    },
});
	$("w-1_list2").sortable("destroy");
$('.day').removeClass('holiday')
$('li').removeClass('nolesson').removeClass('window').addClass('moveAble').append('<i class="handle"></i><i class="edit"></i>')
$('.edit').click(function(){
	$('#overlay').css('opacity', 1).fadeIn(300)
})
$('.close').click(function(){
	$('#overlay').animate({opacity: 0}, 300, function() {$(this).hide()})
	return false
})