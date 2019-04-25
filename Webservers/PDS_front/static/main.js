
var page = {
    init : function(){
        document.addEventListener('DOMContentLoaded', this.addAllInitCallback.bind(this));
    },

    addAllInitCallback : function(){
        console.log('Init!');
        this.addSubmitFunc.bind(this)();
        this.addEventChangeToInput.bind(this)();
    },

    addSubmitFunc : function(){
        console.log("Add submit!");
        document.getElementById("submit_pid").addEventListener("click", this.searchBtnClick.bind(this));
    },

    addEventChangeToInput : function(){
        console.log("Add change to input btn!");
        document.getElementById('mrn_input').addEventListener("change", this.disableAnlzBtn.bind(this))
    },

    addAnlzFunc :function(){
        document.getElementById("extract-btn").addEventListener("click", page.anlzBtnClick);
    },

    removeAnlzFunc:function(){
        document.getElementById("extract-btn").removeEventListener("click", page.anlzBtnClick);
    },

    removeAllChild : function(node){
        while (node.firstChild) {
            node.removeChild(node.firstChild);
        }
    },

    visible_features : ['date', 'note_id', 'contents'],
    features : ['myelopath' , 'trauma','atrauma', 'non-trauma', 'radiculo', 'pain', 'instabil', 'synho', 'sehyo', 'tenderness', 'fever'],
    pid : undefined,

    createTable : function(answer){
        //creates a <table> element
        var table = document.createElement("table");
        table.setAttribute('id', "result_table");
        table.classList.add('result-table');

        answerLength = answer['Notes'].length;
        visible_feature = page.visible_features;
        features =  page.features;
        visible_feature = visible_feature.concat(features);

        //Currently only display DATE, NOTE ID, and CONTEXT
        var numOfColumns = visible_feature.length;

        // Creating table header
        var tableHeader = document.createElement("tr");
        for (var i = 0; i < numOfColumns; i++){
            var featureName = visible_feature[i];
            var headerCell = document.createElement("th");
            headerCell.classList.add(featureName);
            var cellText = document.createTextNode(featureName);
            headerCell.appendChild(cellText);
            tableHeader.appendChild(headerCell);
        }
        table.appendChild(tableHeader);

        // creating rows and  add visit notes element
        for( var i = 0; i < answerLength; i++){
            var row = document.createElement("tr");
            row.classList.add('result_row');
            row.classList.add('empty-result');

            //create columns in row
            for (var j = 0; j < numOfColumns; j++){
                var colName = visible_feature[j];
                var cell = document.createElement("td");
                cell.classList.add(colName);

                if (features.indexOf(colName) !== -1) {
                     cell.classList.add('extractedFeature');
                }

                var paragraph = document.createElement("p");
                var noteElement = answer['Notes'][i];
                var cellText = document.createTextNode(noteElement[colName]?noteElement[colName]:"");

                paragraph.appendChild(cellText);
                cell.appendChild(paragraph);
                row.appendChild(cell);
            }
            table.appendChild(row);

            //div.innerHTML = "<p> "+ answer['Notes'][i]["date"] + "    "+ answer['Notes'][i]["note_id"]+"    "+ answer['Notes'][i]["contents"] + "</p>";
            //var visit_note = document.getElementById('visit_note').appendChild(div);
            //setTimeout(function() { console.log(div.innerHTML) }, 10000);
        }

        return table;
    },

    featureSuccessCallback : function(answer, row){
        // console.log("Success!", answer);
        //Toggle class 'result', 'no-result'
        row.classList.remove('no-result');
        row.classList.add('result');

        function showResult(resultElement){
            //result element : 'clause', 'pain', 'instability', 'sent'

            console.log(resultElement);

            for(var i=0;i<page.features.length; i++){
                feature_name = page.features[i];
                var target_p = row.querySelector('td.' + feature_name + ' p');
                page.removeAllChild(target_p);

                var child_p = document.createElement('p');
                child_p.classList.add('extracted-feature');

                if(resultElement[feature_name] === '+'){
                    child_p.classList.add('positive');
                    child_p.innerText = '+';
                    var reference_div = document.createElement('div');
                    reference_div.classList.add('reference');
                    var sent = resultElement['sent'];
                    var clause = resultElement['clause'];
                    var start_position = sent.indexOf(clause);
                    var end_position = start_position + clause.length;
                    reference_div.innerHTML = sent.substring(0, start_position) + "<span class='clause'>" + resultElement['clause'] + "</span>" + sent.substring(end_position, sent.length);;
                    child_p.appendChild(reference_div);

                }else if (resultElement[feature_name] === '-'){
                    child_p.classList.add('negative');
                    child_p.innerText = '-';

                    var reference_div = document.createElement('div');
                    reference_div.classList.add('reference');
                    var sent = resultElement['sent'];
                    var clause = resultElement['clause'];
                    var start_position = sent.indexOf(clause);
                    var end_position = start_position + clause.length;
                    reference_div.innerHTML = sent.substring(0, start_position) + "<span class='clause'>" + resultElement['clause'] + "</span>" + sent.substring(end_position, sent.length);;
                    child_p.appendChild(reference_div);
                }
                target_p.appendChild(child_p);
            }

        }

        answer['Features'].forEach(showResult);

        page.toggleFeatureLoadingGif(row);
    },

    featureFailCallback : function(answer, row, callback){
        // TODO: when fail answer
        // console.log("Fail!", answer);

        //Toggle class 'result', 'no-result'
        row.classList.remove('result');
        row.classList.add('no-result');

        page.toggleFeatureLoadingGif(row);
    },

    featureExtractCallback : function(xhr, row){
        if (xhr.status === 200) {
            answer = xhr.responseText;
            answer = JSON.parse(answer);

            // console.log(answer);
            result_status = answer['Result'];

            if(result_status === "Success"){
                this.featureSuccessCallback(answer, row);
            }else{
                this.featureFailCallback(answer, row);
            }

        } else {
            alert('Request failed.  Returned status of ' + xhr.status);
        }
    },


    result_success_callback : function(answer, callback){

        // get the reference for the body
        var targetDiv = document.getElementById("result_box");

        // remove all child of VISITtablediv
        page.removeAllChild(targetDiv);

        targetDiv.classList.remove("visitHiddenTableClass");

        // create result table
        var tb1 = page.createTable(answer);

        // Add result table to div1
        targetDiv.appendChild(tb1);

        if (callback){
            callback();
        }

    },

    result_fail_callback : function(answer, callback){
        //Hide or delete Loading box
        var targetDiv = document.getElementById("result_box");
        targetDiv.classList.remove("visitHiddenTableClass");

        //Delete all result contents
        page.removeAllChild(targetDiv);

        // Create and add "No result" element.
        var div = document.createElement('div');
        div.classList.add('no-result-div');
        div.innerHTML = "<p> No result - reason : "+ answer['reason'] +"("+ page.pid.value + ")" + "</p>";
        var result_box = document.getElementById('result_box').appendChild(div);

        if (callback){
            callback();
        }
    },

    loadHxCallback : function(xhr, pid) {
        // console.log(this);

        if (xhr.status === 200) {
            answer = xhr.responseText;
            answer = JSON.parse(answer);

            // console.log(answer);
            result_status = answer['Result'];

            if(result_status === "Success"){
                this.result_success_callback(answer, page.toggleTableLoadingGif);
                page.enableAnlzBtn();
            }else{
                this.result_fail_callback(answer, page.toggleTableLoadingGif);
            }

        } else {
            alert('Request failed.  Returned status of ' + xhr.status);
        }
    },

    enableAnlzBtn : function(){
        AnlzBtn = document.querySelector("div.search-row .search-box .extract-feature-btn");
        page.enableBtn(AnlzBtn);
    },

    disableAnlzBtn : function(){
        console.log('Disabled!');
        AnlzBtn = document.querySelector("div.search-row .search-box .extract-feature-btn");
        page.disableBtn(AnlzBtn);
    },

    disableBtn:function(btn){
        a_link = btn.querySelector('a');
        // console.log(a_link);max-height: 500px;
        a_link.classList.add('sandy-one');
        a_link.setAttribute('disabled', true);
        page.removeAnlzFunc();
    },

    enableBtn : function(btn){
        a_link = btn.querySelector('a');
        // console.log(a_link);
        a_link.classList.add('sandy-one');
        a_link.removeAttribute('disabled');
        page.addAnlzFunc();
    },

    searchBtnClick : function(){
        console.log("Search!");

        // add loading gif
        var targetDiv = document.getElementById("result_box");
        page.removeAllChild(targetDiv);
        page.toggleTableLoadingGif();

        // alert('stop!');

        // ajax call
        var xhr = new XMLHttpRequest();
        page.pid = document.getElementById('mrn_input').value;
        // console.log(page.pid);
        var pid = page.pid;

        // console.log(pid);
        url = new URL("/", api_host_ip);
        url = new URL('/patient_history?Pid=' + pid, url);

        xhr.open('GET', url);
        xhr.onload = this.loadHxCallback.bind(page, xhr, pid);
        xhr.send();
    },

    getRowsFromResultTable : function(start_id, end_id){
        var resultRows = document.querySelectorAll("tr.result_row");

        if (end_id < 0){
            end_id = resultRows.length;
        }

        var top5Rows = [];
        for (var i=start_id; i < end_id; i++){
            top5Rows.push(resultRows[i]);
        }
        return top5Rows;
    },

    anlzRow : function(row){

        var getContentsFromRow = function(row){
            var note_str = row.getElementsByClassName(['contents']);
            //console.log(note_str);
            note_str = note_str[0].innerText;
            return note_str;
        };

        page.toggleFeatureLoadingGif(row);

        var pid = page.pid;
        var F_list = page.features.join("__");
        var note = getContentsFromRow(row);

        var formData = new FormData();
        formData.append("note", note);
        formData.append("F_list", F_list);
        formData.append("mrn", pid);

        // ajax call
        var xhr = new XMLHttpRequest();
        url = new URL("/", api_host_ip);
        url = new URL('/feature_extract', url);
        xhr.open('POST', url);
        xhr.onload = page.featureExtractCallback.bind(page, xhr, row);
        xhr.send(formData);
    },

    anlzBtnClick : function(){
        console.log("Analyze!");

        // Get 5 first rows query for extraction
        targetRows = page.getRowsFromResultTable(0, 100);
        targetRows.forEach(page.anlzRow);

    },

    // For making loading gif file
    toggleTableLoadingGif : function (){
        txt = document.getElementById("result_box").innerText;
        if (!txt) {
            // console.log(txt);
            document.getElementById("process").innerText = "Processing ...";
            document.getElementById("loading").src = "./static/ajax-loader.gif";
        }else{
            // console.log(txt);
            document.getElementById("process").innerText = "";
            document.getElementById("loading").removeAttribute('src');
        }
    },

    toggleFeatureLoadingGif : function(row){
        function hasClass (element, className){
            return (' ' + element.className + ' ').indexOf(' ' + className+ ' ') > -1;
        }

        first_feature = row.querySelector("." + page.features[0]);
        // console.log("Toggle!", row.className);


        if (hasClass(row, 'empty-result')) {
            row.classList.remove('empty-result');
            var img = document.createElement('img');
            img.src = "./static/loading-feature.gif";
            first_feature.appendChild(img)
        }else{
            console.log("Remove child!");
            row.classList.add('empty-result');
            page.removeAllGifChild(first_feature);
        }
    },

    removeAllGifChild : function(target_element){
        var gif = target_element.getElementsByTagName('img')[0];
        target_element.removeChild(gif);
    }

};

page.init();

