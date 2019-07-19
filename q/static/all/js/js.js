/**
 * Created by gys on 26.03.2017.
 */
GOOGLE_API_KEY = "";
function all() {
    $(document).ready(function () {
        $("#menu_activator").on("click", function () {
            $("#sidenav-overlay").css("width","100%");
            $("#slide-out").removeClass('leftmenu_close');
            $("#slide-out").addClass('leftmenu_open')
        });
        $("#sidenav-overlay").on("click", function () {
            $("#sidenav-overlay").css("width","0%");
            $("#slide-out").removeClass('leftmenu_open');
            $("#slide-out").addClass('leftmenu_close')
        });
    });
}
function pay_price() {
    $(document).ready(function () {
       $("label[for='pay_price']").on("click", function(){
           $("div#collapsepay").css("display","block");
           $("div#collapsepay").animate({
               "opacity":1
           },500)
       }) ;
       $("label[for='free_price']").on("click", function(){
           $("div#collapsepay").animate({
               "opacity":0
           },500);
           setTimeout(function(){
               $("div#collapsepay").css("display","none");
           },500)
       }) ;
    });
}
function cost_check() {
    $(document).ready(function () {
        var i=0;
       $("label[for='id_paid']").on("click", function(){
           i++;
           if (i % 2 != 0) {
               $("form#costslide").css("display", "block");
               $("form#costslide").animate({
                   "opacity": 1
               }, 500)
           }
           else{
               $("form#costslide").animate({
                   "opacity":0
               },500);
               setTimeout(function(){
                   $("form#costslide").css("display","none");
               },500)
           }
       }) ;
    });
}
function sliderfound(){
    $('#slider').slider({
        value: 50,
        max:1000,
        create: setInputsFromSlider,
        slide: setInputsFromSlider,
        stop: setInputsFromSlider
    });

    function setInputsFromSlider() {
        $('#slideVal').val($('#slider').slider("value"));
    }

    $('#flat-slider').slider({
        values: [0, 1000],
        range: true,
        max:1000,
        create: setInputsFrom2Slider,
        slide: setInputsFrom2Slider,
        stop: setInputsFrom2Slider
    });

    function setInputsFrom2Slider() {
        $('#rangeMin').val($('#flat-slider').slider("values", 0));
        $('#rangeMax').val($('#flat-slider').slider("values", 1));
    }

    $('input').change(function(e) {
        switch (this.id) {
            case "rangeMin":
            case "rangeMax":
                var index = (this.id == "rangeMax") ? 1 : 0;
                $('#flat-slider').slider("values", index, $(this).val());
                break;
            case "slideVal":
                $('#slider').slider("value", $(this).val());
                break;
        }
    });
    $("#flat-slider").on('mouseup', function(){
        search();
    });
}
function mask() {
    $("#begin_date").mask("99.99.2099");
    $("#end_date").mask("99.99.2099");
    $("#id_phone").mask("8(999)999-99-99");
    $("#id_date_of_birth").mask("99.99.9999");
}
function datepicker() {
    var now = new Date();
   $('#id_meeting_date_time_0').pickadate({
        selectYears: true,
        min: [now.year,now.month,now.day],
        selectMonths: true,
        selectYears: 2,
        closeOnSelect: false,
        closeOnClear: false
   });
   $("#id_begin_date_time_0").pickadate({
        selectYears: true,
        min: [now.year,now.month,now.day],
        selectMonths: true,
        selectYears: 2,
        closeOnSelect: false,
        closeOnClear: false
   });
   $("#id_end_date_time_0").pickadate({
        selectYears: true,
        min: [now.year,now.month,now.day],
        selectMonths: true,
        selectYears: 2,
        closeOnSelect: false,
        closeOnClear: false
   });
   $("#id_meeting_date_time_0").attr("placeholder",'*Дата');
   $("#id_meeting_date_time_1").attr("placeholder",'*Время');
   $("#id_begin_date_time_0").attr("placeholder",'*Дата');
   $("#id_begin_date_time_1").attr("placeholder",'*Время');
   $("#id_end_date_time_0").attr("placeholder",'*Дата');
   $("#id_end_date_time_1").attr("placeholder",'*Время');
   $("#id_meeting_date_time_1").clockpicker({
       autoclose: false,
       donetext: 'ГОТОВО'
   });
   $("#id_begin_date_time_1").clockpicker({
       autoclose: false,
       donetext: 'ГОТОВО'
   });
   $("#id_end_date_time_1").clockpicker({
       autoclose: false,
       donetext: 'ГОТОВО'
   });
}
function search(){
    $(document).ready(function () {
        var status = 0;
        for (var j = 0; j < 3;j++){
            if ($("input[name='status']").eq(j).prop('checked') == true){
                status = j+1;
            }
        }
        var name = $('input[name="quest_name"]').val();
        var town = $('input[name="quest_town"]').val();
        var quen_categories = $("input[name='category']").length;
        var categories = '';
        for(var i = 0; i< quen_categories; i++ ){
             if ($("input[name='category']").eq(i).prop('checked') == true){
                 categories = $("label[name='category']").eq(i).text()+"|"+ categories
             }
        }
        var have_group='';
        if($('input#group').prop("checked")){
            have_group = 'True';
        }
        else {
            if($('input#only').prop("checked")){
                have_group = 'False'
            }
            else{
                have_group = 'None'
            }
        }
        var pay_status='';
        var min_pay =0;
        var max_pay = 0;
        if($('input#pay_price').prop("checked")){
            pay_status = 'True';
            min_pay =$("input#rangeMin").val();
            max_pay =$("input#rangeMax").val()
        }
        else {
            if($('input#free_price').prop("checked")){
                pay_status = 'False'
            }
            else{
                pay_status = 'None'
            }
        }
        var have_password = $("input#q_password").prop('checked');
        var begin_date = $("input#begin_date").val();
        var end_date = $("input#end_date").val();
        $.get("get_filter_quests/", {name:name, status:status, town:town,
            have_group:have_group, have_password:have_password, begin_date:begin_date,categories:categories, end_date:end_date,
            pay_status:pay_status, min_pay:min_pay, max_pay:max_pay}, function(data){
            $("#filter_quests").empty();
            $("#filter_quests").html(data);
        })
    });
}
function photousergallery() {
    var initPhotoSwipeFromDOM = function(gallerySelector) {

        // parse slide data (url, title, size ...) from DOM elements
        // (children of gallerySelector)
        var parseThumbnailElements = function(el) {
            var thumbElements = el.childNodes,
                numNodes = thumbElements.length,
                items = [],
                figureEl,
                linkEl,
                size,
                item;

            for(var i = 0; i < numNodes; i++) {

                figureEl = thumbElements[i]; // <figure> element

                // include only element nodes
                if(figureEl.nodeType !== 1) {
                    continue;
                }

                linkEl = figureEl.children[0]; // <a> element

                size = linkEl.getAttribute('data-size').split('x');

                // create slide object
                item = {
                    src: linkEl.getAttribute('href'),
                    w: parseInt(size[0], 10),
                    h: parseInt(size[1], 10)
                };



                if(figureEl.children.length > 1) {
                    // <figcaption> content
                    item.title = figureEl.children[1].innerHTML;
                }

                if(linkEl.children.length > 0) {
                    // <img> thumbnail element, retrieving thumbnail url
                    item.msrc = linkEl.children[0].getAttribute('src');
                }

                item.el = figureEl; // save link to element for getThumbBoundsFn
                items.push(item);
            }

            return items;
        };

        // find nearest parent element
        var closest = function closest(el, fn) {
            return el && ( fn(el) ? el : closest(el.parentNode, fn) );
        };

        // triggers when user clicks on thumbnail
        var onThumbnailsClick = function(e) {
            e = e || window.event;
            e.preventDefault ? e.preventDefault() : e.returnValue = false;

            var eTarget = e.target || e.srcElement;

            // find root element of slide
            var clickedListItem = closest(eTarget, function(el) {
                return (el.tagName && el.tagName.toUpperCase() === 'FIGURE');
            });

            if(!clickedListItem) {
                return;
            }

            // find index of clicked item by looping through all child nodes
            // alternatively, you may define index via data- attribute
            var clickedGallery = clickedListItem.parentNode,
                childNodes = clickedListItem.parentNode.childNodes,
                numChildNodes = childNodes.length,
                nodeIndex = 0,
                index;

            for (var i = 0; i < numChildNodes; i++) {
                if(childNodes[i].nodeType !== 1) {
                    continue;
                }

                if(childNodes[i] === clickedListItem) {
                    index = nodeIndex;
                    break;
                }
                nodeIndex++;
            }



            if(index >= 0) {
                // open PhotoSwipe if valid index found
                openPhotoSwipe( index, clickedGallery );
            }
            return false;
        };

        // parse picture index and gallery index from URL (#&pid=1&gid=2)
        var photoswipeParseHash = function() {
            var hash = window.location.hash.substring(1),
            params = {};

            if(hash.length < 5) {
                return params;
            }

            var vars = hash.split('&');
            for (var i = 0; i < vars.length; i++) {
                if(!vars[i]) {
                    continue;
                }
                var pair = vars[i].split('=');
                if(pair.length < 2) {
                    continue;
                }
                params[pair[0]] = pair[1];
            }

            if(params.gid) {
                params.gid = parseInt(params.gid, 10);
            }

            return params;
        };

        var openPhotoSwipe = function(index, galleryElement, disableAnimation, fromURL) {
            var pswpElement = document.querySelectorAll('.pswp')[0],
                gallery,
                options,
                items;

            items = parseThumbnailElements(galleryElement);

            // define options (if needed)
            options = {

                // define gallery index (for URL)
                galleryUID: galleryElement.getAttribute('data-pswp-uid'),

                getThumbBoundsFn: function(index) {
                    // See Options -> getThumbBoundsFn section of documentation for more info
                    var thumbnail = items[index].el.getElementsByTagName('img')[0], // find thumbnail
                        pageYScroll = window.pageYOffset || document.documentElement.scrollTop,
                        rect = thumbnail.getBoundingClientRect();

                    return {x:rect.left, y:rect.top + pageYScroll, w:rect.width};
                }

            };

            // PhotoSwipe opened from URL
            if(fromURL) {
                if(options.galleryPIDs) {
                    // parse real index when custom PIDs are used
                    // http://photoswipe.com/documentation/faq.html#custom-pid-in-url
                    for(var j = 0; j < items.length; j++) {
                        if(items[j].pid == index) {
                            options.index = j;
                            break;
                        }
                    }
                } else {
                    // in URL indexes start from 1
                    options.index = parseInt(index, 10) - 1;
                }
            } else {
                options.index = parseInt(index, 10);
            }

            // exit if index not found
            if( isNaN(options.index) ) {
                return;
            }

            if(disableAnimation) {
                options.showAnimationDuration = 0;
            }

            // Pass data to PhotoSwipe and initialize it
            gallery = new PhotoSwipe( pswpElement, PhotoSwipeUI_Default, items, options);
            gallery.init();
        };

        // loop through all gallery elements and bind events
        var galleryElements = document.querySelectorAll( gallerySelector );

        for(var i = 0, l = galleryElements.length; i < l; i++) {
            galleryElements[i].setAttribute('data-pswp-uid', i+1);
            galleryElements[i].onclick = onThumbnailsClick;
        }

        // Parse URL and open gallery if it contains #&pid=3&gid=1
        var hashData = photoswipeParseHash();
        if(hashData.pid && hashData.gid) {
            openPhotoSwipe( hashData.pid ,  galleryElements[ hashData.gid - 1 ], true, true );
        }
    };

    // execute above function
    initPhotoSwipeFromDOM('.my-gallery');
}
function pinSymbol(color, bordercolor) {
    return {
        path: 'M 0,0 C -2,-20 -10,-22 -10,-30 A 10,10 0 1,1 10,-30 C 10,-22 2,-20 0,0 z M -2,-30 a 2,2 0 1,1 4,0 2,2 0 1,1 -4,0',
        fillColor: color,
        fillOpacity: 1,
        strokeColor: bordercolor,
        strokeWeight: 2,
        scale: 1
   };
}
function cirSymbol(color, bordercolor) {
    return {
        path: 'M 0, 0' +
        'm -6, 0' +
        'a 6,6 0 1,0 12,0' +
        'a 6,6 0 1,0 -12,0',
        fillColor: color,
        fillOpacity: 1,
        strokeColor: bordercolor,
        strokeWeight: 12,
        scale: 1
   };
}
function getstreet(data, k) {
    request = k.results[0].formatted_address;
    request = request.split(",");
    request = String(request[0]) + String(request[1]);
    $("input[name='q_address-" + data[0] + "-" + data[1] + "']").val(request);
    $("label[for='q_address-" + data[0] + "-" + data[1] + "']").addClass("active")
}
function getstreet2(data, k) {
    request = k.results[0].formatted_address;
    request = request.split(",");
    request = String(request[0]) + String(request[1]);
    $("input[name='q_address-" + data[0] + "']").val(request);
    $("label[for='q_address-" + data[0] + "']").addClass("active")
}
function initMap(POST) {
    $(document).ready(function(){
        var uluru = {lat: 56.634407, lng: 47.899878};
        var map = new google.maps.Map(document.getElementById('mapcontainer'), {
          zoom: 13,
          center: uluru
        });
        var markers = [];
        var group_markers = new Array();
        $('#id_town').change(function(){
            town = this.value;
            $.post('https://maps.googleapis.com/maps/api/geocode/' +
                'json?address=' +
                'Россия+'+ town +
                '&key='+GOOGLE_API_KEY,{}, function (data) {
                var latlng = data.results[0].geometry.location;
                map = new google.maps.Map(document.getElementById('mapcontainer'), {
                  zoom: 13,
                  center: {lat: latlng.lat, lng: latlng.lng}
                });
            });
        });
        var meeting_marker;
        for(var h=1; h <= 20; h++){
            group_markers[h] = new Array();
            for(var j=1; j<= 10; j++){
                group_markers[h][j] = 0;
            }
        }
        $('#id_meeting_point').change(function(){
            town = $('#id_town').val();
            address = this.value;
            if (meeting_marker != undefined){
                    meeting_marker.setMap(null);
            }
            $.post('https://maps.googleapis.com/maps/api/geocode/' +
                'json?address=' +
                'Россия'+ town + '+' + address +
                '&key='+GOOGLE_API_KEY,{}, function (data) {
                var latlng = data.results[0].geometry.location;
                meeting_marker = new google.maps.Marker({
                    position: {lat: latlng.lat, lng: latlng.lng} ,
                    map: map,
                    icon: pinSymbol('#fff','#9A45BF')
                });
            });
        });
        if(POST){
            town = $('#id_town').val();
                address = $('#id_meeting_point').val();
                $.post('https://maps.googleapis.com/maps/api/geocode/' +
                    'json?address=' +
                    'Россия'+ town + '+' + address +
                    '&key='+GOOGLE_API_KEY,{}, function (data) {
                    var latlng = data.results[0].geometry.location;
                    meeting_marker = new google.maps.Marker({
                        position: {lat: latlng.lat, lng: latlng.lng} ,
                        map: map,
                        icon: pinSymbol('#fff','#9A45BF')
                    });
                });
            if ($("input#id_have_group").prop('checked') == false){
                wayps = $('input[second_name="q_address"]').length;
                for(var i=1; i <= wayps; i++){
                    sh = Number($('input[name="sh-'+ i +'"]').val());
                    dl = Number($('input[name="dl-'+ i +'"]').val());
                    if((sh != 0) && (dl !=0)){
                        markers[i] = new google.maps.Marker({
                              position: {lat: sh, lng: dl} ,
                              map: map
                        });
                        $.ajax({
                            url:'https://maps.googleapis.com/maps/api/geocode/' +
                            'json?address=' +
                            sh + ' ' + dl +
                            '&key='+GOOGLE_API_KEY,
                            success: getstreet2.bind([],[i])
                        });
                    }
                }
            }
            else{
                groups = $('div.group').length;
                for(i=1; i <= groups; i++){
                    len_waypoints = $('input[name="q-col-'+ i +'"]').length;
                    group_color = $('input[name="group_color"]').eq(i-1).val();
                    for(j=1; j <= len_waypoints; j++){
                        sh = Number($('input[name="sh-'+ i +'-'+ j +'"]').val());
                        dl = Number($('input[name="dl-'+ i +'-'+ j +'"]').val());
                        if((sh != 0) && (dl !=0)){
                            group_markers[i][j] = new google.maps.Marker({
                                position: {lat: sh, lng: dl} ,
                                map: map,
                                icon: pinSymbol('#' + group_color, '#' + group_color)
                            });
                            $.ajax({
                                url:'https://maps.googleapis.com/maps/api/geocode/' +
                                'json?address=' +
                                sh + ' ' + dl +
                                '&key='+GOOGLE_API_KEY,
                                success: getstreet.bind([],[i,j])
                            });
                        }
                    }
                }
            }
        }
        $("#waypoints").on('change',"input[second_name='q_address']", function () {
            if ($("input#id_have_group").prop('checked') == false){
                street = this.value;
                number = $(this).attr('id').split("-");
                number = number[1];
                if (markers[number] != undefined){
                    markers[number].setMap(null)
                }
                town = $('#id_town').val();
                $.post('https://maps.googleapis.com/maps/api/geocode/' +
                    'json?address=' +
                    'Россия+'+ town+ '+' + street +
                    '&key='+GOOGLE_API_KEY,{}, function (data) {

                    if(data.results[0] != undefined){
                        var latlng = data.results[0].geometry.location;
                        markers[number] = new google.maps.Marker({
                              position: {lat: latlng.lat, lng: latlng.lng} ,
                              map: map
                        });

                        if(street == ''){
                            $("input[name=sh-" +number + "]").val('');
                            $("input[name=dl-" +number + "]").val('');
                        }
                        else {
                            $("input[name=sh-" +number + "]").val(latlng.lat);
                            $("input[name=dl-" +number + "]").val(latlng.lng);
                        }
                    }
                    else {
                            $("input[name=sh-" +number + "]").val('');
                            $("input[name=dl-" +number + "]").val('');
                    }
                });
            }
            else{
                number = $(this).attr('id').split("-");
                group = number[1];
                waypoint_id = number[2];
                street = this.value;
                town = $('#id_town').val();
                color = $('div.divider[for=' + group + ']').attr('style').split(":");
                color = color[1];
                if ((group_markers[group][waypoint_id] != undefined) && (group_markers[group][waypoint_id] != 0)){
                    group_markers[group][waypoint_id].setMap(null)
                }
                $.post('https://maps.googleapis.com/maps/api/geocode/' +
                    'json?address=' +
                    'Россия+'+ town+ '+' + street +
                    '&key='+GOOGLE_API_KEY,{}, function (data) {
                    var latlng = data.results[0].geometry.location;
                    group_markers[group][waypoint_id] = new google.maps.Marker({
                          position: {lat: latlng.lat, lng: latlng.lng} ,
                          map: map,
                          icon: pinSymbol(color,color)
                    });
                    if(street == ''){
                        group_markers[group][waypoint_id].setMap(null);
                        $("input[name=sh-" +group + "-" + waypoint_id +"]").val('');
                        $("input[name=dl-" +group + "-" + waypoint_id +"]").val('');
                    }
                    else {
                        $("input[name=sh-" +group + "-" + waypoint_id + "]").val(latlng.lat);
                        $("input[name=dl-" +group + "-" + waypoint_id + "]").val(latlng.lng);
                    }
                });
            }
        });
        $("input#id_have_group").change(function(){
            if ($("input#id_have_group").prop('checked') == true){
                for(var h=1; h<=markers.length; h++){
                    markers[h].setMap(null);
                }
                markers = [];
            }
            else{
                for(var t =1; t <= group_markers.length; t++){
                    for(var y=1; y<= group_markers.length; y++){
                        if((group_markers[t][y] != 0) && (group_markers[t][y] != undefined)){
                            group_markers[t][y].setMap(null);
                        }
                    }
                }
                group_markers = new Array();
                for(h=1; h <= 20; h++){
                    group_markers[h] = new Array();
                    for(var j=1; j<= 10; j++){
                        group_markers[h][j] = 0;
                    }
                }
            }
        });
    });
}
function waypoints() {
     $(document).ready(function(){
         var i=0;
         var j=0;
         var gid=$('input[name="q-col"]').length;;
         var onlyid=$('input[name="q-col"]').length;

         $("label[for='id_have_group']").on("click", function(){
             i++;
             if ($("input#id_have_group").prop('checked') == false){
                i = 1
             }
             else{
                i = 2
             }
             if (i % 2 != 0) {
                gid = 2;
                $.post('get_html_groups/',{option:2, gid:gid},function(data){
                    $("#waypoints").html(data);
                })
             }
             else{
                onlyid=1;
                $.post('get_html_groups/',{option:1,oid:onlyid},function(data){
                    $("#waypoints").html(data);
                });
             }
         });
         $("#add_waypoint").on("click", function(){
             j++;
             if ($('input#id_have_group').prop("checked")) {
                 gid = gid + 2;
                   $.post('get_html_groups/',{option:2, gid:gid},function(data){
                       $("#waypoints").append(data);
                   })
             }
             else{
                 onlyid = onlyid +1;
                 $.post('get_html_groups/',{option:1, oid:onlyid},function(data){
                       $("#waypoints").append(data);
                 });
             }
         });
         var group_waypoint_id = 0;

         $("#waypoints").on('click',"#add_group_waypoint", function(){
              var group = $(this).attr('for');
              group_waypoint_id = $("#group_waypoints_list-" + group).children('.group_waypoint').length + 1;
              $.post('get_html_group_waypoint/',{group_id:group, group_waypoint_id:group_waypoint_id},function(data){
                    $("#group_waypoints_list-" + group).append(data)
              })
         });
     });
}
function waypoints2() {
     $(document).ready(function(){
         var i=0;
         var j=0;
         var gid=$('input[name="q-col"]').length;
         var onlyid=$('input[name="q-col"]').length;

         $("label[for='id_have_group']").on("click", function(){
             i++;
             if ($("input#id_have_group").prop('checked') == false){
                i = 1
             }
             else{
                i = 2
             }
             if (i % 2 != 0) {
                gid = 2;
                $.post('../../create/get_html_groups/',{option:2, gid:gid},function(data){
                    $("#waypoints").html(data);
                })
             }
             else{
                onlyid=1;
                $.post('../../create/get_html_groups/',{option:1,oid:onlyid},function(data){
                    $("#waypoints").html(data);
                });
             }
         });
         $("#add_waypoint").on("click", function(){
             j++;
             if ($('input#id_have_group').prop("checked")) {
                 gid = gid + 2;
                   $.post('../../create/get_html_groups/',{option:2, gid:gid},function(data){
                       $("#waypoints").append(data);
                   })
             }
             else{
                 onlyid = onlyid +1;
                 $.post('../../create/get_html_groups/',{option:1, oid:onlyid},function(data){
                       $("#waypoints").append(data);
                 });
             }
         });
         var group_waypoint_id = 0;

         $("#waypoints").on('click',"#add_group_waypoint", function(){
              var group = $(this).attr('for');
              group_waypoint_id = $("#group_waypoints_list-" + group).children('.group_waypoint').length + 1;
              $.post('../../create/get_html_group_waypoint/',{group_id:group, group_waypoint_id:group_waypoint_id},function(data){
                    $("#group_waypoints_list-" + group).append(data)
              })
         });
     });
}
// рендеринг изображения
function renderImage(file) {

 // генерация нового объекта FileReader
  var reader = new FileReader();

 // подстановка изображения в атрибут src
  reader.onload = function(event) {
    the_url = event.target.result;
    $("img#settimg").attr('src',the_url)
  };

 // при считке файла, вызывается метод, описанный выше
  reader.readAsDataURL(file);
}

function renderImageM(file) {
    var reader = new FileReader();

    reader.onload = function(event) {
        the_url = event.target.result;
        $("#download_img").append("<img class='w-50 float-left p-1' src=" + the_url + ">");
    };

    reader.readAsDataURL(file);
}

function QuestImageAvatar(file) {
    var reader = new FileReader();

    reader.onload = function(event) {
        the_url = event.target.result;
        $("img.quest_avatar_img").remove();
        $("#quest_avatar").append("<img class='quest_avatar_img' src=" + the_url + ">");
    };

    reader.readAsDataURL(file);
}
function QuestPhotoItems(files) {
    for(var o=0; o < files.length; o++){
        var reader = new FileReader();

        reader.onload = function(event) {
            the_url = event.target.result;
            $(".list_quest_photos").append("<img class='photo_item col-lg-2 float-left' src=" + the_url + ">");
        };
        reader.readAsDataURL(files[o]);
    }
}
function QuestPhotoItem(file) {
    var reader = new FileReader();

    reader.onload = function(event) {
        the_url = event.target.result;
        $(".list_quest_photos").append("<img class='photo_item col-lg-2 float-left' src=" + the_url + ">");
    };
    reader.readAsDataURL(file);
}
function QuestPhotos(){
    var dropzone = document.getElementById('add_quest_avatar_back');

    dropzone.ondrop = function(e){
        e.preventDefault();
        $(".list_quest_photos").empty();
        quest_photos_input.files = e.dataTransfer.files;
        for(var o=0; o < e.dataTransfer.files.length; o++ ){
            file = e.dataTransfer.files[o];
            QuestPhotoItem(file[0])
        }
    };

    dropzone.ondragover = function(){
        return false;
    };
    dropzone.ondragleave = function(){
        return false;
    }
}
function QuestAvatar(){
    var dropzone = document.getElementById('quest_avatar');

    dropzone.ondrop = function(e){
        e.preventDefault();
        id_avatar.files = e.dataTransfer.files;
        QuestImageAvatar(e.dataTransfer.files[0]);
    };

    dropzone.ondragover = function(){
        return false;
    };
    dropzone.ondragleave = function(){
        return false;
    }
}
function check_code() {
    $(document).ready(function(){
        var try_id = 0;
        $("input#discount").change(function(){
            try_id += 1;
            code = $(this).val();
            if (try_id <= 5){
                $.post('../checkcode/',{code:code},function (data) {
                    if(data.isvalid){
                        $('#discount_per').html(data.discount + '%');
                        $('#discount_rub').html((600 * Number(data.discount) / 100)+ ' руб');
                        $('#itog').html((600 - 600 * Number(data.discount) / 100)+ ' руб')
                    }
                    else{
                        $('#discount_per').html(data.discount + '%');
                        $('#discount_rub').html((600 * Number(data.discount) / 100)+ ' руб');
                        $('#itog').html((600 - 600 * Number(data.discount) / 100)+ ' руб')
                    }
                })
            }
        })
    })
}
function meeting_map(town,address){
    $(document).ready(function(){
        $.post('https://maps.googleapis.com/maps/api/geocode/' +
            'json?address=' +
            'Россия'+ town + '+' + address +
            '&key='+GOOGLE_API_KEY,{}, function (data) {
            var latlng = data.results[0].geometry.location;
            var map = new google.maps.Map(document.getElementById('mapcontainer'), {
                zoom: 15,
                center: {lat: latlng.lat, lng: latlng.lng}
            });
            meeting_marker = new google.maps.Marker({
                position: {lat: latlng.lat, lng: latlng.lng} ,
                map: map,
                icon: pinSymbol('#fff','#9A45BF')
            });
        });
    })
}
function group_log_in() {
    $(document).ready(function(){
        $("button#group_log_in").click(function(){
            quest_id = Number(window.location.pathname.split("/")[2]);
            group_name = $("#group_name").val();
            group_admin_log = $("#admin_group_log").val();
            group_admin_pass = $("#admin_group_pass").val();
            $.post('../group_log_in/',{group_name:group_name, group_admin_log:group_admin_log,
                group_admin_pass:group_admin_pass, quest_id:quest_id},function (data) {
                if(data.correct == undefined){
                    $("#go_cont").html(data);
                }
                else{
                    $("#err").css("display","block");
                }
            });
        })
    })
}
function geo_success(cords,map, you,circleOptions,markerCircle, position) {
    map.panTo(new google.maps.LatLng(position.coords.latitude, position.coords.longitude));
    var lat = position.coords.latitude;
    var lng = position.coords.longitude;
    you.setPosition({lat:lat, lng:lng});
    var _pCord = new google.maps.LatLng({lat:lat, lng:lng});
    for(var i=0; i < cords.length; i++){
        var _kCord = new google.maps.LatLng({lat:cords[i][1], lng:cords[i][0]});
        if(google.maps.geometry.spherical.computeDistanceBetween(_pCord, _kCord) <= 50 ){
            markerCircle[i].fillOpacity = 0.35;
            markerCircle[i].strokeOpacity = 0.8;
        }
        else{
            markerCircle[i].fillOpacity = 0;
            markerCircle[i].strokeOpacity = 0;
        }
    }

}

function geo_error(error) {


}

function quest_go_map(cords) {
    $(document).ready(function(){
        var uluru = {lat: 55.753215, lng: 37.622504};
        var map = new google.maps.Map(document.getElementById('map'), {
            zoom: 17,
            center:uluru
        });
        var you = new google.maps.Marker({
            map: map,
            position:uluru,
            icon: cirSymbol('#1F75FE','rgba(31, 117, 255, 0.2)')
        });
        var markerCircle = [];
        var circleOptions = {
                strokeColor: '#ffbb33',
                strokeOpacity: 0,
                strokeWeight: 2,
                fillColor: '#ffbb33',
                fillOpacity: 0,
                map: map,
                radius: 50
            };
        for(var i=0; i < cords.length; i++){
            markerCircle[i] = new google.maps.Circle(circleOptions);
            markerCircle[i].setCenter({lat:cords[i][1], lng:cords[i][0]})
        }
        navigator.geolocation.watchPosition(geo_success.bind([],cords, map, you, circleOptions,markerCircle), geo_error,{
                                                enableHighAccuracy:true,
                                                timeout: 5000,
                                                maximumAge: 0
                                            })
    })
}
function quest_end(town, cords){
    $(document).ready(function(){
        $.post('https://maps.googleapis.com/maps/api/geocode/' +
            'json?address=' +
            'Россия'+ town +
            '&key=AIzaSyBUYNPWXGurMeIwlE9Q2Hjdl8e31UGvsOQ',{}, function (data) {
            var latlng = data.results[0].geometry.location;
            var map = new google.maps.Map(document.getElementById('mapcontainer'), {
                zoom: 13,
                center: {lat: latlng.lat, lng: latlng.lng}
            });
            var markers = [];
            for(var i=0; i < cords.length; i++){
                markers[i] = new google.maps.Marker({
                    position: {lat:cords[i][1], lng:cords[i][0]},
                    map: map
                });
            }
        });
    });
}
function group_quest_end(town, cords){
    $(document).ready(function(){
        $.post('https://maps.googleapis.com/maps/api/geocode/' +
            'json?address=' +
            'Россия'+ town +
            '&key=AIzaSyBUYNPWXGurMeIwlE9Q2Hjdl8e31UGvsOQ',{}, function (data) {
            var latlng = data.results[0].geometry.location;
            var map = new google.maps.Map(document.getElementById('mapcontainer'), {
                zoom: 13,
                center: {lat: latlng.lat, lng: latlng.lng}
            });
            var markers = new Array();
            for(var j=0; j < Object.keys(cords).length; j++){
                markers[j] = new Array();
                for(var i=0; i < cords[j].length; i++){
                    markers[j][i] = ''
                }
               }
            for(var i=0; i < cords[0].length; i++){
                markers[0][i] = new google.maps.Marker({
                    position: {lat:cords[0][i][1], lng:cords[0][i][0]},
                    map: map
                });
            }
            $("li[name='marker_activate']").on("click", function(){
               number = $(this).attr('for');
               for(var j=0; j < Object.keys(cords).length; j++){
                   for(var i=0; i < cords[j].length; i++){
                       if(markers[j][i] != ''){
                           markers[j][i].setMap(null)
                       }
                   }
               }
               for(var i=0; i < cords[number].length; i++){
                    markers[number][i] = new google.maps.Marker({
                        position: {lat:cords[number][i][1], lng:cords[number][i][0]},
                        map: map
                    });
                }
            });
        });

    });
}
function qpsettings() {
    $('input#qsphoto').on('change',function () {
        if($('input#qsphoto').prop('checked') == true){
            $.post('get_html_checkbox_photo/',{},function(data){
                $("#all_quest_photo").html(data);
            });
        }
        else{
            $.post('get_html_normal_photo/',{},function(data){
                $("#all_quest_photo").html(data);
            });
        }
    });
}


