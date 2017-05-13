var express = require('express');
var app = express();
var fs = require("fs");

var async = require('async');
var request = require('request');
var PythonShell = require('python-shell');
var bodyParser = require('body-parser');
const exec = require('child_process').exec;

app.use(bodyParser.json());

app.get('/', function (req, res) {
  res.send('Hello World!');
});

app.post('/', function(req, res, next) {
    var text = req.body.text;
    var title = req.body.title;

    async.waterfall([
        function (cb){
            var options = {
                mode: 'text',
                pythonOptions: ['-u'],
                args: [text, title]
            };
            PythonShell.run('batch.py', options, function (err, results) {

                if (err) {
                    return cb(err);
                }else{

                    if(results === undefined || typeof(results) == "undefined"){
                        return cb(err);
                    }
                    else{

                        results.shift();
                        return cb(null, results);
                    }
                }
            });
        }, function (topics, cb){
            /* - Grouping out the results from python into an object -*/
            var topic_list = []
            // async.forEachOf(topics, function (value, key, callback) {
            for (var key = 0; key < topics.length; key++){
                if(topics[key] !== "--"){
                    topic_name = topics[key];
                    topics[key] = "--";
                    topic_frequency = topics[key+1];
                    topics[key+1] = "--";
                    topic_score = topics[key+2]
                    topics[key+2] = "--";
                    topic_alias_length = topics[key+3];
                    topics[key+3] = "--";

                    aliases = []
                    sentinel = key + parseInt(topic_alias_length) + 4;
                    for (var i = key+4; i < sentinel; i++){
                        aliases.push(topics[i]);
                        topics[i] = "--";
                    }

                    topic_list.push({
                        'topic': topic_name,
                        'score' : topic_score,
                        'frequency': topic_frequency,
                        'aliases' : aliases
                    });
                    // callback();
                }
                else{
                    // callback();
                }
            }
            return cb(null, topic_list);
            // }, function (err) {
            //     if (err) return cb(err.message);
            //     return cb(null, topic_list); // topic_list -> json format | from_python -> list of strings
            // });
        } // end function
    ], function (err, topics){
        if(err){
            return res.send({
                status: "error",
                data: err
            });
        }
        else{
            return res.send(topics);
        }
    });


});

app.listen(8000, function () {
  console.log('Example app listening on port 8000!');
});

process.on('uncaughtException', function (err) {
    const child = exec('pkill python',(error, stdout, stderr) => {
        process.exit();
    });
});

process.on('SIGINT', function() {
    const child = exec('pkill python',(error, stdout, stderr) => {
        process.exit();
    });
});

process.on('exit', function(code) {
    const child = exec('pkill python',(error, stdout, stderr) => {
        process.exit();
    });
});
