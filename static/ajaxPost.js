$(document).ready(function() {
        $("#downloadPDF").click(function(e) {
        e.preventDefault();
            generatePDF();
            }
        );

        $('#upload').click(function(e) {
            e.preventDefault();
            $("#graph").empty();
            $("#somArea").empty();
            $("#extractedText").empty();
            $("#extractedTFIDF").empty();
            $(".flash").empty();
            $(".flash").hide();
            $("#downloadPDF").hide();
            objHolder = null;
            var formD = new FormData();
            var file = document.getElementById("file");
            formD.append('file', file.files[0]);
            formD.append('useGPU', $('#useGPU').is(':checked'));
            formD.append('mapSide', $('#mapSide').val());            
            $("#working").html("Working on it....");
            $.ajax({
                processData: false,
                data: formD,
                type: 'POST',
                contentType: false,
                success: function(response) {
                    objHolder = response;
                    graphResponse(response);
                },
                error: function(error) {
                    $("#working").html("Didn't work.");
                    if(error.status == 413){
                        $(".flash").html("File is too big.");
                        $(".flash").show();
                    } else {
                        $(".flash").html(error.status+ " " + error.statusText);
                        $(".flash").show();
                    }
                }
            });
        });


});

function pointclick(eventData){
    eventData.preventDefault();
    var pointData = eventData.data;
    $("#extractedText").html(pointData.text);
    var tfidfString = "";
    for(var i = 0; i < pointData.tfIDF.length; i++){
        tfidfString += pointData.tfIDF[i] + ", ";
    }
    tfidfString = tfidfString.slice(0,-2); //remove last ,
    $("#extractedTFIDF").html(tfidfString);
}

function displayCluster(eventData){
    var clusterIndex = eventData.data.cluster;
    $("#somArea .node").hide();
    $("#somArea #node"+clusterIndex).show();
}
var objHolder;
function graphResponse(response){   

    if(response.hasOwnProperty("flaskerror")){
         $(".flash").html(response.flaskerror);
         $(".flash").show();
         $("#working").html("Didn't work.");
         return false;
     }
    var pointCount = 0;
    
    for(var i = 0; i < Object.keys(response.clusters).length; i++){
        $("#graph").append("<div id='graphNode"+i+"' class='graphNode'></div>");
        $("#graphNode"+i).bind("click", {"cluster": i}, displayCluster);
        var str = "";
        str += "<div class='node' id='node"+i+"'>";
        str += "</div>";
        $("#somArea").append(str);
        $("#somArea #node"+i).hide();
        for(var j = 0; j < response.clusters[i].length; j++){
            var pointStr = "";
            pointStr += "<div style='' class='point'><a id='point"+pointCount+"'>";
            pointStr += response.clusters[i][j]; // adding the cluster data
            pointStr += "</a></div>";
            $("#node"+i).append(pointStr);
            var text = response.dataset[response.clusters[i][j]];
            var tfIDF = response.tfIDF[response.clusters[i][j]];
            var pointData = {"cluster": i, "point" : response.clusters[i][j], "text": text, "tfIDF": tfIDF};
            $("#point"+pointCount).bind("click", pointData, pointclick);
            pointCount++;
        }
        var aColor = [Math.floor(Math.random()*256), Math.floor(Math.random()*256), Math.floor(Math.random()*256)]; 
        if(aColor == [0,0,0] || aColor == [255,255,255]){
            aColor = [Math.floor(Math.random()*256), Math.floor(Math.random()*256), Math.floor(Math.random()*256)];
        }
        colors.push(aColor);
        $("#graphNode"+i).css("background-color","rgb("+aColor[0]+","+aColor[1]+","+aColor[2]+")");
    }
    colors.push([0,0,0]); // add color for unclustered data
    var clusterCount = Object.keys(response.clusters).length;
    var sqSide = Math.sqrt(clusterCount);
    $( ".graphNode:nth-child("+sqSide+"n+1)" ).css("clear", "left");
    $("#working").html("Done - " + parseFloat(response.timeTaken).toFixed(4)+" secs.");
    $("#downloadPDF").show();
}

$(window).scroll(function(){
   // $("#graph").css({"margin-top": ($(window).scrollTop()) + "px", "margin-left":($(window).scrollLeft()) + "px"});
   // $("#textarea").css({"margin-top": ($(window).scrollTop()) + "px", "margin-left":($(window).scrollLeft()) + "px"});
});

var colors = [];

function generatePDF(){
    if(typeof(objHolder) == 'undefined'){
        console.log("Not ready to generate PDF.");
        return false;
    }
    var pdf = new jsPDF('p','in','A4');
    var pageHeight = pdf.internal.pageSize.height;
    var margin = 0.5, verticalOffset = margin, lines, size=12;

    for(var i = 0; i < objHolder.dataset.length; i++){
        //find where this has been clustereds
        var fromCluster = Object.keys(objHolder.clusters).length    ;
        for(var j = 0; j < Object.keys(objHolder.clusters).length; j++){
            for(var k = 0; k < objHolder.clusters[j].length; k++){
                if(i === objHolder.clusters[j][k]){
                    fromCluster = j;
                }
            } 
        }
            
            pdf.setTextColor(colors[fromCluster][0], colors[fromCluster][1], colors[fromCluster][2]);
            verticalOffset += 0.5;
            lines = pdf.setFont("Helvetica","")
                        .setFontSize(size)
                        .splitTextToSize(objHolder.dataset[i], 7.5);
            pdf.text(0.5, verticalOffset + size / 72, lines);
            verticalOffset += (lines.length + 0.5) * size / 72;
            
            if(i+1 < objHolder.dataset.length){
            var nextLines = pdf.setFont("Helvetica","")
                        .setFontSize(size)
                        .splitTextToSize(objHolder.dataset[i+1], 7.5);
            if( (verticalOffset + ((nextLines.length + 0.5) * size / 72)) > pageHeight - margin){
                pdf.addPage();
                verticalOffset = margin;            
            }
            }
        }
    pdf.save('Test.pdf');
}