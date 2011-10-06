//Function used for check date. Made for calendarClickBind function
function checkDate(calYear,calMonth,calDay) {
    if(calYear>1900&&calYear<2999)
        if(calMonth>-1&&calMonth<12)
            if(calDay>0&&calDay<32)
                return true;
    return false;
}

//Function used for make sure pop-up calendar have the same value with date input field 
function calendarClickBind(prefix) {

$("#formfield-"+prefix).find(".caltrigger").bind("click",function(){

$("#"+prefix+"-calendar").data("dateinput").hide();
calDay=($("#"+prefix+"-day").val());
calMonth=($("#"+prefix+"-month").val())-1;
calYear=($("#"+prefix+"-year").val());
if(checkDate(calYear,calMonth,calDay))
    $("#"+prefix+"-calendar").data("dateinput").setValue(calYear,calMonth,calDay);
else
    $("#"+prefix+"-calendar").data("dateinput").today();
$("#"+prefix+"-calendar").data("dateinput").show();
});

}

(function($) {

    loadCodes = function(thisObj, id, type, level){
        var next_widget = '#'+id+(level+1);

        if (thisObj.val() != '#') {
            var data_source = '@@anzsrc-codes?type='+type+'&code='+thisObj.val();
            $(next_widget).load(data_source, function() { $(this).enable() });
            $(next_widget).parent().nextAll().find('select[id^='+id+']').html(' ').attr('disabled', 'disabled');
        } else {
            thisObj.parent().nextAll().find('select[id^='+id+']').html(' ').attr('disabled', 'disabled');
        }
        $('#'+id+'add').attr('disabled','disabled').css('opacity','0.5');
    };

    //Function:
    //id: prefix for drop-down menus
    //type: type of codes to load, passed to server
    //levels:  how many levels are there in total? (3 select boxes = 3 levels)
    //target_field: short ID of the DGF widget to target
    bootstrapCodeFields = function(id, type, levels, target_field) {
        var identifier = '#'+id;
        var addButton = $(identifier+'add');
        var lastMenu = $(identifier+(levels-1));

        loadCodes($(identifier+0), id, type, -1);
        for (var i=0; i<=(levels-2); i++) {
            (function(i) {
                $(identifier+i).change(function() { loadCodes($(this), id, type, i); } );
            }(i));
        }
        lastMenu.change(function() {
            if (this.value == '#') {
                addButton.attr('disabled','disabled').css('opacity','0.5');
            } else { 
                addButton.enable().css('opacity','1.0');
            } 
        });

        addButton.click(function() {
            $(identifier+'AA-widgets-'+target_field+'-widgets-query').val(lastMenu.val()).search();
            	
        });

    };

    $(document).ready(function() {
        $('input[name=form.widgets.research_themes:list]').not(':last').click(
                function() {
                    $('input[name=form.widgets.research_themes:list]').last().attr("checked", false);
                }
        );
        $('input[name=form.widgets.research_themes:list]').last().click(
                function() {
                    $('input[name=form.widgets.research_themes:list]').not(':last').attr("checked", false);
                }
        );

        calendarClickBind("form-widgets-temporal_coverage_start");
        calendarClickBind("form-widgets-temporal_coverage_end");
    });

})(jQuery);
