fs     = require 'fs'
{exec} = require 'child_process'

staticDir = './mnlp/lionmap/static/'
assetDir = './assets/'
coffeeDir  = "#{assetDir}coffee/"
coffeeFiles = fs.readdirSync coffeeDir
jsDir = "#{staticDir}js/generated/"
appCoffee = "#{jsDir}mnlp.coffee"
cssDir = "#{staticDir}css/generated/"
sassDir = "#{assetDir}sass/"
sassFiles = fs.readdirSync sassDir

String::endsWith = (str) -> if @match(new RegExp "#{str}$") then true else false

task 'build', 'Build single application file from source files', ->
    invoke 'coffee2js'
    invoke 'sass2css'
          
task 'coffee2js', 'Compile coffeescript to javascript', ->
    Toaster = require( 'coffee-toaster' ).Toaster
    toasting = new Toaster __dirname,
        c:true
        d:true
        config:
            # => SRC FOLDERS AND VENDORS
            folders:
                'assets/coffee': 'app'

            vendors:[]

            # OPTIONS
            bare: false
            packaging: true
            expose: 'window'
            minify: false

            # RELEASING
            httpfolder: 'static/js/generated'
            release: "mnlp/lionmap/static/js/generated/mnlp.js"
            debug: "mnlp/lionmap/static/js/generated/mnlp-debug.js"
    toasting.build
    
          
task 'sass2css', 'Compile sass to css', ->
  appContents = new Array
  remaining = sassFiles.length
  for file, index in sassFiles when file.endsWith '.scss' then do (file, index) ->
    cssName = file.split('.')[0]
    exec "sass #{sassDir}#{file} #{cssDir}#{cssName}.css", (err, stdout, stderr) ->
        throw err if err
        console.log stdout + stderr