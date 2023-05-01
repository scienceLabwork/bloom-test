import bitarray as bitA
import mmh3
import hashlib
from flask import Flask, flash, request, redirect, url_for, render_template, Response
app = Flask(__name__)
# Filter Length
filter_len = 37
# Filter Declaration
hash = bitA.bitarray(filter_len)
hash.setall(0)
# Variables for storing some of the intermediate steps
history = {}
K = 3
wordRecord = []
N = 25
dummy = {}  
prob = 65.37
countOfSetBits = 0
constraint = 8
explanation = ''
dummy_explanation = '! No operation performed !'
reset_explanation = '! Reset operation performed !'

# def newValues():
#     pass

# Function to reset the entire filter
def resetCache():
    global hash
    global wordRecord
    global history
    hash = bitA.bitarray(filter_len)
    wordRecord.clear()
    hash.setall(0)
    history.clear()

# Functions to generate hash
def generate_hash1(word):
    generated_hash = mmh3.hash(word)
    generated_hash = generated_hash % filter_len
    return generated_hash

def generate_hash2(word):
    hash_func = hashlib.sha256()
    hash_func.update(word.encode())
    hash_func.update(word.encode())
    return int(hash_func.hexdigest(), 16) % filter_len

def generate_hash3(word):
    # self defined
    generated_hash = 0
    for i in word:
        generated_hash = (generated_hash * 10) + (ord(i) % filter_len)
    generated_hash = generated_hash % filter_len
    return generated_hash    

# Functions to perform these hash functions
def perform_hash1(word):
    global hash
    global countOfSetBits
    generated_hash = generate_hash1(word)
    if hash[generated_hash] == False:
        countOfSetBits = countOfSetBits + 1
    hash[generated_hash] = bool(1)

def perform_hash2(word):
    global hash
    global countOfSetBits
    generated_hash  = generate_hash2(word)
    if hash[generated_hash] == False:
        countOfSetBits = countOfSetBits + 1
    hash[generated_hash] = bool(1)

def perform_hash3(word):
    global hash
    global countOfSetBits
    generated_hash = generate_hash3(word)
    if hash[generated_hash] == False:
        countOfSetBits = countOfSetBits + 1
    hash[generated_hash] = bool(1)

def add_cache(word):
    perform_hash1(word)
    perform_hash2(word)
    perform_hash3(word)

# Functions to generate the explanation/steps performed in achieving the respective results

def generateExplanation(results):
    global explanation
    explanation = ''
    explanation = explanation + "Steps Followed: \n\n"
    explanation = explanation + "Step 1: Generated hash of the search key are :-\n Hash 1 - "+ str(results['Hash 1']) + "\n Hash 2 - "+ str(results['Hash 2']) + "\n Hash 3 - "+ str(results['Hash 3']) + " \n\n "
    explanation = explanation + "Step 2: Now check whether all the bits at the above position are set or not\n\n"
    if results['Found'] == True:
        explanation = explanation + "The search key " + str(results['Search Key']) + " found in the filter. \n"
        explanation = explanation + "Step 3: In this case all the bits are set, this means there is probability that the search key is present in the cache\n"
    else:
        explanation = explanation + "Step 3: In this case all the bits are not set, it implies that the search key is not present in the cache (100 % probability)\n"

# Starting Function of the algorithm

def check_cache(word):
    global wordRecord
    try :
        history[word] = history[word] + 1
    except:
        history[word] = int(1) 
    added = False
    # bool reset = False       
    if history[word] == constraint:
        add_cache(word)
        wordRecord.append(word)
        added = True
        if countOfSetBits >= int(0.65 * filter_len):
            resetCache()
    pos1 = generate_hash1(word)
    pos2 = generate_hash2(word)
    pos3 = generate_hash3(word)
    check = bool(hash[pos1] and hash[pos2] and hash[pos3])
    results = {'Search Key' : word,'Found' : check,'Hash 1' : pos1,'Hash 2' : pos2,'Hash 3' : pos3}  
    generateExplanation(results)
    results['explanation'] = str(explanation)
    print(results)
    if added :
        results['New Acitivity'] = 'Search Key Added'    
    return results;      

def generateError():
    return {'Error':'Invalid / No String Searched'}


# Rendering various templates as per the requirements
# Main Page
@app.route("/", methods=['POST', 'GET'])
def first():
    if request.method == 'POST':
        global filter_len 
        filter_len = int(request.form['idM'])
        global constraint 
        constraint = int(request.form['idC'])
        global N
        N = int(request.form['idN'])
        global prob
        # print(((1 - ((1 - (1/filter_len))**(N*3)))**3))
        prob = ((1 - ((1 - (1/filter_len))**(N*3)))**3) * 100
        resetCache()
        # return 
        render_template("index.html",hash = hash, result = dummy,filter_len = filter_len, wordRecord = wordRecord,explanation = dummy_explanation, m = filter_len, c = constraint, n = N, prob = prob)
        return redirect("home")
    else:
        return render_template("first.html")
@app.route("/home", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        if request.form['btnSubmit'] != "SEARCH":
            resetCache()
            return render_template("index.html",hash = hash, result = dummy,filter_len = filter_len, wordRecord = wordRecord,explanation = reset_explanation, m = filter_len, c = constraint, n = N, prob = prob)
            # return redirect("index.html")
        else:
            word_received = request.form['word']
            if word_received == '':
                return render_template("index.html",hash = hash, result = generateError(),filter_len = filter_len, wordRecord = wordRecord,explanation = dummy_explanation, m = filter_len, c = constraint, n = N, prob = prob)
            check = check_cache(word_received)
            return render_template("index.html",hash = hash, result = check,filter_len = filter_len, wordRecord = wordRecord,explanation = explanation, m = filter_len, c = constraint, n = N, prob = prob)
    else:
        return render_template("index.html",hash = hash, result = dummy,filter_len = filter_len, wordRecord = wordRecord,explanation = dummy_explanation, m = filter_len, c = constraint, n = N, prob = prob)
# About Page
@app.route("/about")
def about():
    return render_template("about.html")

# Concept Page
@app.route("/concept")
def concept():
    return render_template("concept.html", m = filter_len, c = constraint, n = N, prob = prob)

# References Page 
@app.route("/references")
def references():
    return render_template("references.html")

if __name__ == "__main__":
    app.run(debug = False,host='0.0.0.0', port= 5454)
