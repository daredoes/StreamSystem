var RATINGS = {
    {{ c.RATED_GOOD }}: {
        false: '../static/images/check_blank.png',
        true:  '../static/images/check_filled.png'
    },
    {{ c.RATED_BAD }}: {
        prompt: 'Please explain how this volunteer performed poorly:',
        false: '../static/images/lookofdisapproval.jpg',
        true:  '../static/images/lookofdisapproval_selected.jpg'
    },
    {{ c.RATED_GREAT }}: {
        prompt: 'Please explain how this volunteer went above and beyond:',
        false: '../static/images/aplus_blank.jpg',
        true:  '../static/images/aplus_filled.jpg'
    }
};

var renderRating = function (shift, $td) {
    shift = typeof shift === 'string' ? SHIFTS[shift] : shift;
    $td = ($td || $('#rating' + shift.id)).addClass('rating').data('shift', shift);
    $.each([{{ c.RATED_GOOD }}, {{ c.RATED_BAD }}, {{ c.RATED_GREAT }}], function (i, rating) {
        $td.append(
            $('<img/>').attr('src', RATINGS[rating][shift.rating === rating])
                       .attr('title', shift.comment)
                       .data('rating', rating));
    });
    return $td;
};

var setupRatingClickHandler = function () {
    $(document.body).on('click', 'td.rating img', function (event) {
        var $img = $(event.target);
        var shift = $img.parent().data('shift');
        var rating = $img.data('rating');
        var comment = '';
        while (comment === '' && RATINGS[rating].prompt) {
            comment = prompt(RATINGS[rating].prompt);
        }
        if (comment !== null ) {
            var params = {shift_id: shift.id, rating: rating, comment: comment, csrf_token: csrf_token};
            $.post('../jobs/rate', params, function (json) {
                $img.parent().find('img').each(function (){
                    var r = $(this).data('rating');
                    $(this).attr('title', comment)
                           .attr('src', RATINGS[r][r == rating]);
                });
            }, 'json');
        }
    });
};

var setStatus = function (shiftId, status) {
    var $status = $(status);
    var statusVal = parseInt($status.val());
    $.post('../jobs/set_worked', {id: shiftId, status: statusVal, csrf_token: csrf_token}, function (result) {
        if (result.error) {
            alert(result.error);
        } else {
            var statusLabel = _(result.shifts).filter({id: shiftId}).pluck('worked_label').first() || 'Unexpected Error';
            $status.parent().empty()
                .append('<i>' + statusLabel + '</i> &nbsp; ')
                .append($undoForm('../jobs/undo_worked', {id: shiftId}));
            if (statusVal === {{ c.SHIFT_WORKED }}) {
                renderRating(shiftId);
            }
        }
    });
};

var $undoForm = function (path, params, linkText) {
    var $form = $('<form method="POST"></form>').attr("action", path);
    $.each($.extend(params, {csrf_token: csrf_token}), function (name, value) {
        $('<input type="hidden" />').attr("name", name).attr("value", value).appendTo($form);
    });
    var $undoLink = $('<a href="#"></a>').text(linkText || "Undo").click(function (e) {
        e.preventDefault();
        $form.submit();
    });
    return $().add($undoLink).add($form);
};
