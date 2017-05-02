# deep-donald

[@DeepDonald_](https://twitter.com/DeepDonald_)

### Question

The purpose of this project was to create a self-contained Twitter bot that could take some seed text in the form of a tweet and respond in the style of Donald Trump.

### Data Collection and Cleaning

A complete archive of Trump's tweets was readily available thanks to the work of [bpb27](https://github.com/bpb27/trump-tweet-archive) who maintains http://www.trumptwitterarchive.com/.  The key fields contained in the JSON formatted files were 'source' (the device used to send the tweet) and 'text' (the tweet's content). 

We know that not all Trump tweets are created equal; thanks to the work of [David Robinson](http://varianceexplained.org/r/trump-tweets/) (and others), we know tweets sourced from 'Twitter for Android' are from the Donald himself and not a staffer.

Taking this into account, we were left with a trimmed down corpus of roughly ~15k tweets out of the ~31k total available.  This was further reduced to ~7k with the removal of any "old-school retweet" tweets.  These follow the format of "RT@USER..." response.  Since most of the text in these tweets is from other Twitter users and not Trump, they would not be useful for training our model.

Additional text was gleaned from several interviews and speech transcripts (AP, CBS, etc).  The total aggregate corpus for training was 1.5 MB.

The speech transcripts were mostly cleaned by hand as they presented many unique challenges.  The data had many artifacts, interviewer questions and comments had to be removed, and markers for applause/laughter/etc had to be removed.  

These steps were laborious but necessary to make sure the model output was as high quality as possible.  Poorly cleaned/standardized inputs led to poor output initially; time spent on this step paid the highest dividends toward the final product.

### Features

For the traditional modeling portion of this project, TF-IDF vectorization was used for feature generation.  Because this type of vectorization emphasizes the importance of rarer words, it gives us the most empirically useful data for classification.

### Modeling

#### Text Generation

I implemented Torch-RNN (https://github.com/jcjohnson/torch-rnn) to handle all the text generation for this script.  Character level generation, rather than word level, was used so that user inputs wouldn't have to be limited to words already present in the "Donald Trump lexicon".  This also allows us to generate output on topics Trump has never publicly commented on before.  We are also saved from having to spell check/significantly sanitize the inputs into the model.

Larger models consistently outperformed smaller models while length of training time didn't always translate into better results.  The final model was trained with the following hyperparameters `-rnn_size 512 -num_layers 3` for the default number of epochs.  Iterations were done through several other setups; often the limiting factor was computing power.

#### Tweet Classification

The Tweet classification model is a voting classifier estimator built with a logistic regression, random forest and extra trees model.  The base model score was .15 while the test score was .89, indicating a very significant improvement via modeling.  XGBoost did not perform as expected and was thus not included in the final classifier.  

The models and TF-IDF transformer were pickled to allow easy implementation in the twitter response script.

#### Tweet Responses

The Twitter reply framework was built off [sample-twitter-autoreply](https://github.com/twitterdev/sample-python-autoreply).  A few challenges presented themselves during this implementation.  I was able to utilize bash for the text generation through the `subprocess` library.  10 sample tweets were generated (the RNN still struggles to produce grammatically accurate sentences with every output) and these were then transformed (after trimming them based on their punctuation) and then run through the voting classifier.  The highest probability sample was selected as the response to the user's query.  

### Conclusions

I really enjoyed threading all of the existing projects and data together to provide a new service/output during this project.  I borrowed heavily from many authors to provide a unique product 


### Future Direction

