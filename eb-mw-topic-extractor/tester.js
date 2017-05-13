var fs = require('fs');
var async = require('async');
var request = require('request');
var PythonShell = require('python-shell');

async.waterfall([
    function (cb) {
        fs.readFile('ids', 'utf8', function (err, data) {
          if (err) throw err;
          ids = data.split('\n')
          return cb(null, ids);
        });
    },
    function (ids, cb) {

        var args = process.argv;
        // console.log('args: ', args[2]);
        var debug = false;
        if(args.length == 2){
            console.log("Testing mode.");
        }
        else if (args.length == 3 && args[2] == "debug"){
            debug = true;
            console.log("Debug mode.");
        }

        article_ids = ids;
        if(ids.length > 1){
            console.log("There are "+article_ids.length+" articles to be tested.")
        }
        else{
            console.log('One article to be tested.')
        }

        var counter = 1;


        async.eachLimit(article_ids, 1, function(article_id, eCb){
            var main_url = "http://mw-source-api-env.elasticbeanstalk.com/v0/articles/"+article_id;

            request.get(main_url, function (err, response, body){
                if(!err && response.statusCode == 200){
                    var body = JSON.parse(body);
                    var article = body.data;

                    console.log(counter+". "+article_id+" "+article.url);
                    counter ++;
                    var options = {
                        mode: 'text',
                        // pythonOptions: ['-u'],
                        args: [article.text, article.title]
                    };
                    console.log('-a-');
                    PythonShell.run('batch.py', options, function (err, results) {
                        if (err){
                            console.log('error @ pythonsell');
                            eCb(err);
                        }
                        else{
                            if(results === undefined){
                                console.log('results is undefined');
                                eCb(new Error('Results undefined'));
                            }
                            else{
                                console.log('python run done');
                                results.shift();
                                if(debug){
                                    console.log(results);
                                }
                                var topic_list = [];
                                for (var key = 0; key < results.length; key++){
                                    if(results[key] !== "--"){
                                        topic_name = results[key];
                                        results[key] = "--";
                                        topic_frequency = results[key+1];
                                        results[key+1] = "--";
                                        topic_score = results[key+2]
                                        results[key+2] = "--";
                                        topic_alias_length = results[key+3];
                                        results[key+3] = "--";

                                        aliases = []
                                        sentinel = key + parseInt(topic_alias_length) + 4;
                                        for (var i = key+4; i < sentinel; i++){
                                            aliases.push(results[i]);
                                            results[i] = "--";
                                        }

                                        // topic_list.push({
                                        //     'topic': topic_name,
                                        //     'score' : topic_score,
                                        //     'frequency': topic_frequency,
                                        //     'aliases' : aliases
                                        // });

                                        var topic = topic_name + " > "+topic_score +":";

                                        if(aliases.length !== 0){
                                            aliases.forEach(function (alias){
                                                topic = topic + alias+"; "
                                            });
                                        }

                                        topic_list.push(topic)
                                    }

                                } // endfor
                                if(debug === false){
                                    console.log(topic_list);
                                }
                                console.log('-NOTHING FOLLOWS');
                            }//else if results is not undefined
                            eCb();
                        } // else if there's not err
                    }); // pythonshell end
                } // endif
                else{
                    return eCb(err);
                }
            }); // request end

        }, function(err){
            if(err){
                console.log(err);
                return cb();
            }
            else{
                return cb();
            }

        });

    }
], function (err){
    if(err){
        console.log(err);
    }
});