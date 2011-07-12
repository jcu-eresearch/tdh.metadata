(function($) {

    loadCodes = function(thisObj, id, type, level){
        var next_widget = '#'+id+(level+1);

        if (thisObj.val() != '#') {
            var data_source = '/@@anzrcs-codes?type='+type+'&code='+thisObj.val();
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
            $(identifier+'AA-widgets-'+target_field).val(lastMenu.val()).parent().change();
        });

    };

})(jQuery);
