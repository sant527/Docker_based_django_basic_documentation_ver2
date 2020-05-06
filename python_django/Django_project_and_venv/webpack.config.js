var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');


//the below are the common properties
common = {
  context: __dirname,


  /* PLUGINS NOTE:
  we have installed webpack-bundle-tracker.  npm install --save-dev webpack webpack-bundle-tracker. So we have to add this to the configuration 
  filename will reside where manager.py resides
  Because: django-webpack-loader (python) package setttings.py we set the path as below

  WEBPACK_LOADER = {
      'DEFAULT': {
          'BUNDLE_DIR_NAME': '',  #we want to have multiple entry in webpack so we keep this blank.
          'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
          #BASE_DIR is your Django project directory. The same directory where manage.py is located.
      }
  }
  Form above we have to ensure the absolute path of webpack-stats.json is same as os.path.join(BASE_DIR, 'webpack-stats.json')
  */

  plugins: [
    new BundleTracker({filename: './basic_django/webpack-stats.json'}),
  ],

  /* MODULE Note
  we have installed babel-loader: This is a webpack helper which allows to transpile Javascript files with babel and webpack. It uses babel under the hood
  What the below configuration does is that for every file with a js or jsx extension, excluding the node_modules folder and it's content, webpack uses babel-loader to transpile the ES6 code to ES5. 
  */

  module: {
    rules: [
      {
        test: /.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      }
    ]
  },

  /* RESOLVE NOTE
  Webpack uses resolve.extensions to generate all the possible paths to the module, e.g.

  function getPaths(module) {
      return ['', '.js', '.css'].map(ext => module + ext);
  }

  getPaths('./somefile'); // ['./somefile', './somefile.js', './somefile.css']

  getPaths('./somefile.js'); // ['./somefile.js', './somefile.js.js', './somefile.js.css']

  Webpack would then proceed to lookup each of those paths until it finds a file.
  */

  resolve: {
    extensions: ['*', '.js', '.jsx']
  }

}

/* ENTRY OUTPUT EXAMPLE NOTE
Example entry ouput object which will be used in the array for module exports
entry_output1 = {

  entry: {
    'polls/js/bundles/index':  path.resolve(__dirname, 'basic_django/polls_example_for_webpack_and_reactjs/polls/static/polls/js/index.js'),
    'polls/js/bundles/questions':  path.resolve(__dirname, 'basic_django/polls_example_for_webpack_and_reactjs/polls/static/polls/js/questions.js'),
   },

  output: {
    path: path.join(__dirname)+"/basic_django/polls_example_for_webpack_and_reactjs/polls/static/", // add / at the end
    filename: "[name]-[hash].js",
  }
}
*/

entry_output1 = {

  entry: {
    'polls/js/bundles/index':  path.resolve(__dirname, 'basic_django/polls_example_for_webpack_and_reactjs/polls/static/polls/js/index.js'),
    'polls/js/bundles/questions':  path.resolve(__dirname, 'basic_django/polls_example_for_webpack_and_reactjs/polls/static/polls/js/questions.js'),
   },

  output: {
    path: path.join(__dirname)+"/basic_django/polls_example_for_webpack_and_reactjs/polls/static/", // add / at the end
    filename: "[name]-[hash].js",
  }
}


/* MODULE EXPORTS ARRAY NOTE
 Why are we using array. Because we want different output folders which is not possible
 with single object
*/

module.exports = [
  {
    name: "somename",
    context: common.context,
    entry: entry_output1.entry,
    output: entry_output1.output,
    plugins: common.plugins,
    module: common.module,
    resolve: common.resolve,
  }
]





/* HOW MULTIPLE ENTRY AND OUTPUT WORK NOTE
How to set multiple file entry and output in project with webpack?
Webpack: path as the entry name: 
=======
common = {
  context: __dirname,

  plugins: [
    new BundleTracker({filename: './basic_django/webpack-stats.json'}),
  ],
>>>>>>> Stashed changes

  module: {
    rules: [
      {
        test: /.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      }
    ]
  },

  resolve: {
    extensions: ['*', '.js', '.jsx']
  }

}

entry_output1 = {

  entry: {
    'polls/js/bundles/index':  path.resolve(__dirname, 'basic_django/polls_example_for_webpack_and_reactjs/polls/static/polls/js/index.js'),
    'polls/js/bundles/questions':  path.resolve(__dirname, 'basic_django/polls_example_for_webpack_and_reactjs/polls/static/polls/js/questions.js'),
   },

  output: {
    path: path.join(__dirname)+"/basic_django/polls_example_for_webpack_and_reactjs/polls/static/", // add / at the end
    filename: "[name]-[hash].js",
  }
}


module.exports =[
	{
	  name: "polls",
	  context: common.context,
	  entry: entry_output1.entry,
	  output: entry_output1.output,
	  plugins: common.plugins,
	  module: common.module,
	  resolve: common.resolve,
	}

]

/*
Before:
home
└── web_dev
    └── DO_NOT_DELETE_djang_basic_documentation_part2
        └── basic_django
            └── polls_example_for_webpack_and_reactjs
                ├── __init__.py
                ├── hare.py
                ├── models.py
                └── polls
                    ├── __init__.py
                    ├── admin.py
                    ├── apps.py
                    ├── fixtures
                    ├── migrations
                    ├── models.py
                    ├── static
                    │   └── polls
                    │       └── js
                    │           ├── index.js
                    │           └── questions.js
                    ├── templates
                    ├── tests.py
                    ├── urls.py
                    └── views.py


AFTER*******************************

 19:38:00  simha  /home/web_dev/DO_NOT_DELETE_djang_basic_documentation_part2   master ✘ ✹ ✭ 
$ tree --noreport --fromfile <<EOF                      
`tree -f -i -n -F --noreport /home/web_dev/DO_NOT_DELETE_djang_basic_documentation_part2/basic_django/polls_example_for_webpack_and_reactjs | grep -E -v 'templates/.+|migrations/.+|fixtures/.+|^\.$'`
EOF
.
└── home
    └── web_dev
        └── DO_NOT_DELETE_djang_basic_documentation_part2
            └── basic_django
                └── polls_example_for_webpack_and_reactjs
                    ├── __init__.py
                    ├── hare.py
                    ├── models.py
                    └── polls
                        ├── __init__.py
                        ├── admin.py
                        ├── apps.py
                        ├── fixtures
                        ├── migrations
                        ├── models.py
                        ├── static
                        │   └── polls
                        │       └── js
                        │           ├── bundles
                        │           │   ├── index-8ea5b4e40178f2c800ee.js
                        │           │   └── question-8ea5b4e40178f2c800ee.js
                        │           ├── index.js
                        │           └── questions.js
                        ├── templates
                        ├── tests.py
                        ├── urls.py
                        └── views.py


*/


// How to run it
/*

$ ./node_modules/.bin/webpack --config webpack.config.js
Hash: f321a5521d75ab142c8c
Version: webpack 4.41.3
Child polls:
    Hash: f321a5521d75ab142c8c
    Time: 1189ms
    Built at: 12/23/2019 6:28:19 PM
                                              Asset     Size  Chunks                         Chunk Names
       /polls/bundles/index-f321a5521d75ab142c8c.js  128 KiB       0  [emitted] [immutable]  /polls/bundles/index
    /polls/bundles/question-f321a5521d75ab142c8c.js  130 KiB       1  [emitted] [immutable]  /polls/bundles/question
    Entrypoint /polls/bundles/index = /polls/bundles/index-f321a5521d75ab142c8c.js
    Entrypoint /polls/bundles/question = /polls/bundles/question-f321a5521d75ab142c8c.js
    [7] ./basic_django/polls_example_for_webpack_and_reactjs/polls/static/polls/js/index.js 280 bytes {0} [built]
    [8] ./basic_django/polls_example_for_webpack_and_reactjs/polls/static/polls/js/questions.js 3.32 KiB {1} [built]
        + 7 hidden modules
    
    WARNING in configuration
    The 'mode' option has not been set, webpack will fallback to 'production' for this value. Set 'mode' option to 'development' or 'production' to enable defaults for each environment.
    You can also set it to 'none' to disable any default behavior. Learn more: https://webpack.js.org/configuration/mode/

 18:28:20  simha  /home/web_dev/DO_NOT_DELETE_djang_basic_documentation_part2   master ✘ ✹ ✭ 
$ 

webpack-stats.json
{
  "status": "done",
  "chunks": {
    "/polls/bundles/index": [
      {
        "name": "/polls/bundles/index-f321a5521d75ab142c8c.js",
        "path": "/home/web_dev/DO_NOT_DELETE_djang_basic_documentation_part2/basic_django/polls_example_for_webpack_and_reactjs/polls/static/polls/bundles/index-f321a5521d75ab142c8c.js"
      }
    ],
    "/polls/bundles/question": [
      {
        "name": "/polls/bundles/question-f321a5521d75ab142c8c.js",
        "path": "/home/web_dev/DO_NOT_DELETE_djang_basic_documentation_part2/basic_django/polls_example_for_webpack_and_reactjs/polls/static/polls/bundles/question-f321a5521d75ab142c8c.js"
      }
    ]
  }
}


<<<<<<< Updated upstream
ALSO ANOTHER EXAMPLE:


NOT SINGLE PAGE APP:
We are not creating single page APP. We will have separate .js file for each view

We will configure our webpack in such a way that it will have different entry points and output points.
MULTIPLE ENTRIES
For having multiple entry points we have to mention the path in the key name
The entry name should be the similar to the django notatio

BEFORE:
                    ├── static
                    │   └── polls
                    │       └── js
                    │           ├── index.js
                    │           └── questions.js

AFTER:
                        ├── static
                        │   └── polls
                        │       └── js
                        │           ├── bundles
                        │           │   ├── index-8ea5b4e40178f2c800ee.js
                        │           │   └── question-8ea5b4e40178f2c800ee.js
                        │           ├── index.js
                        │           └── questions.js

So example:

  entry: {
    'polls/js/bundles/index':  path.resolve(__dirname, 'basic_django/polls_example_for_webpack_and_reactjs/polls/static/polls/js/index.js'),
    'polls/js/bundles/questions':  path.resolve(__dirname, 'basic_django/polls_example_for_webpack_and_reactjs/polls/static/polls/js/questions.js'),
   },

  output: {
    path: path.join(__dirname)+"/basic_django/polls_example_for_webpack_and_reactjs/polls/static/", // add / at the end
    filename: "[name]-[hash].js",
  }


And mention the root folder for output.

MULTIPLE OUTPUTS
For having mutliple outputs we have to use array of configs.

Example:

module.exports =[
  {
    name: "polls",
    context: common.context,
    entry: entry_output1.entry,
    output: entry_output1.output,
    plugins: common.plugins,
    module: common.module,
    resolve: common.resolve,
  },
           {
    name: "login",
    context: common.context,
    entry: entry_output2.entry,
    output: entry_output2.output,
    plugins: common.plugins,
    module: common.module,
    resolve: common.resolve,             
           }

]

And entry_output1 is:
entry_output1 = {

  entry: {
    'polls/js/bundles/index':  path.resolve(__dirname, 'basic_django/polls_example_for_webpack_and_reactjs/polls/static/polls/js/index.js'),
    'polls/js/bundles/questions':  path.resolve(__dirname, 'basic_django/polls_example_for_webpack_and_reactjs/polls/static/polls/js/questions.js'),
   },

  output: {
    path: path.join(__dirname)+"/basic_django/polls_example_for_webpack_and_reactjs/polls/static/", // add / at the end
    filename: "[name]-[hash].js",
  }
}


And common is:

common = {
  context: __dirname,

  plugins: [
    new BundleTracker({filename: './basic_django/webpack-stats.json'}),
  ],

  module: {
    rules: [
      {
        test: /.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      }
    ]
  },

  resolve: {
    extensions: ['*', '.js', '.jsx']
  }

}

*/


//How to copy properties from one object to another
// normal js

// for(var k in firstObject) secondObject[k]=firstObject[k];

// ES6 spread operator
// //const thirdObject = {
//    ...firstObject,
//    ...secondObject   
// }
// Works in Chrome, this is ES6, you will need Babel or some ES6 transpiler currently. In the future all browser are expected to support this syntax.
