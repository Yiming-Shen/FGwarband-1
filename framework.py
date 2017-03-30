import httpcodes
import logging
import json
import os
import pickle
from flask import Flask, request, render_template, redirect, g, send_from_directory, url_for

# Create exportable app
app = Flask(__name__)
app.troops = {'Augment Gorilla': {'Move':8, 'Fight':3, 'Shoot':0, 'Shield':10, 'Morale':2, 'Health':8, 'Cost':20, 'Notes':'Animal, Cannot carry treasure or items'},
'Lackey': {'Move':6, 'Fight':2, 'Shoot':0, 'Shield':10, 'Morale':-1, 'Health':10, 'Cost':20, 'Notes':'Melee Weapon'}, 
'Security': {'Move':6, 'Fight':2, 'Shoot':1, 'Shield':12, 'Morale':2, 'Health':12, 'Cost':80, 'Notes':'Blaster, Blade'}, 
'Engineer': {'Move':4, 'Fight':0, 'Shoot':3, 'Shield':12, 'Morale':2, 'Health':10, 'Cost':60, 'Notes':'Blaster, Repair Kit'}, 
'Medic': {'Move':5, 'Fight':0, 'Shoot':0, 'Shield':12, 'Morale':3, 'Health':10, 'Cost':50, 'Notes':'Blade, Medkit'}, 
'Commando': {'Move':8, 'Fight':4, 'Shoot':0, 'Shield':10, 'Morale':4, 'Health':12, 'Cost':100, 'Notes':'Stealth Suit, Blade, Needle Gun'}, 
'Combat Droid': {'Move':3, 'Fight':2, 'Shoot':4, 'Shield':14, 'Morale':0, 'Health':14, 'Cost':150, 'Notes':'Mechanoid, Dual Blaster, Claws'},               
}
app.wizard = {'Captain': {'Move':5, 'Fight':2, 'Shoot':2, 'Shield':12, 'Morale':4, 'Health':12, 'Cost':0,  'Skillset': [], 'Specialism':None, 'Items':[], 'Experience':0}}
app.apprentice = {'Ensign': {'Move':7, 'Fight':0, 'Shoot':-1, 'Shield':10, 'Morale':2, 'Health':8,'Skillset': [], 'Specialism':None, 'Cost':250, 'Items':[], 'Experience':0}}
app.specialisms = [ 'Engineering', 'Psychology', 'Marksman', 'Tactics', 'Melee', 'Defence' ]
app.skillsets = { 'Engineering' : ['Repair', 'Sabotage', 'Augment'], 'Psychology': [ 'Bolster', 'Terror', 'Counter'], 'Marksman': ['Aim', 'Pierce', 'Reload'], 'Tactics': ['Squad', 'Ambush', 'Surround'], 'Melee': ['Block', 'Risposte', 'Dual'], 'Defence': ['Shield', 'Sacrifice', 'Resolute'] }
app.weapon = [ 'Blaster', 'Needle Gun', 'Blade', 'Cannon', 'Whip']
app.cost = { 'Blaster':5, 'Needle Gun':12, 'Blade':3, 'Cannon':15, 'Whip':5 }
app.loggeduser = ''



@app.route('/', methods=['GET'])
def welcome_page():
    return app.send_static_file('index.html'), httpcodes.OK

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    users = pickle.load(
        open(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users"), "users"), "rb"))
    if request.method == 'GET':
        if app.loggeduser == "":
            return render_template('login.html', accounts=users), httpcodes.OK
        else:
            return redirect(url_for("myaccount"))
    if request.method == 'POST':
        name = request.form['user']
        app.loggeduser = name
        return redirect(url_for("myaccount"))
        


@app.route('/myaccount', methods=['GET', 'POST'])
def myaccount():
    if request.method == 'GET':
        if app.loggeduser == "":
           return redirect(url_for("welcome_page"))
        else:
            bands = os.listdir(
                       os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser))
            return render_template('myaccount.html', name=app.loggeduser, bands=bands), httpcodes.OK
    if request.method == 'POST':
        app.loggeduser = ''
        return redirect(url_for("welcome_page"))


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    users = pickle.load(
         open(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users"), "users"), "rb"))
    if request.method == 'GET':
        return render_template('register.html', accounts=users), httpcodes.OK
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        users[name] = password
        app.loggeduser = name
        pickle.dump(users,
                    open(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users"), "users"),
                         "wb"))
        os.mkdir(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser))
        return redirect(url_for("new_warband"))
                               
 


                              
@app.route('/view', methods=['GET'])
def view_warband():
    
    users = pickle.load(
         open(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users"), "users"), "rb"))
    public_band = dict()
    for user in users.keys():
        public_band[user] = []
        bandlist = os.listdir(
                       os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), user))
        for band in bandlist:
            loadedband = pickle.load(
                          open(os.path.join(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), user), band), "rb"))
            if loadedband['public'] == 'true':
                public_band[user].append(band)
    for item in public_band.keys():
        if public_band[item] == []:
            public_band.pop(item)
    if request.method == 'GET':
        if app.loggeduser == "":
           return redirect(url_for("welcome_page"))
        else:
           return render_template('view.html', public_band = public_band), httpcodes.OK

                               
@app.route('/view/<user>/<band>', methods=['GET'])
def view_given_warband(user, band):

    loadedband = pickle.load(open(os.path.join(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), user), band), "rb"))
    if request.method == 'GET':
        if app.loggeduser == "":
           return redirect(url_for("welcome_page"))
        else:
           return render_template('viewband.html', band=loadedband,  people=app.troops, wizard=app.wizard, apprentice=app.apprentice, specs = app.specialisms, skills = app.skillsets, weaps = app.weapon, weapcost = app.cost), httpcodes.OK
               


    
    
def sumband(createdband):
    total = 0;
    for item in   createdband['Captain']['Items']:
        if item != 'Empty':
            total = total + app.cost[item]
    if 'Ensign' in createdband.keys():
        total = total + 250
        for item in   createdband['Ensign']['Items']:  #should be 'Ensign'
            if item != 'Empty':
                total = total + app.cost[item]
    for troop in createdband['Troops']:
        total = total + app.troops[troop]['Cost']
    return total



@app.route('/new', methods=['GET','POST'])
def new_warband():
    if request.method == 'GET':
       if app.loggeduser == "":
           return redirect(url_for("welcome_page"))
       else:
           return render_template('blankband.html', people=app.troops, wizard=app.wizard, apprentice=app.apprentice, specs = app.specialisms, skills = app.skillsets, weaps = app.weapon, weapcost = app.cost), httpcodes.OK
    if request.method == 'POST':
       
       publicstat = request.form['publicstat']
       bandname = request.form['bandname']
       totalmoney = request.form['totalmoney']
       capspec = request.form['capspec']
       capskill = request.form['capskill']
       capweap = request.form['capweap']
       capweap2 = request.form['capweap2']
       troops = json.loads(request.form['troops']) 
       bought = json.loads(request.form['bought']) 
       
       createdband = dict()
       createdband['public'] = publicstat
       createdband['totalmoney'] = totalmoney
       createdband['Bought'] = bought
       createdband['Name'] = bandname
       createdband['Captain'] = dict(app.wizard['Captain'])
       createdband['Captain']['Specialism'] = capspec

       createdband['Captain']['Skillset'] = []
       createdband['Captain']['Skillset'].append(capskill)
       
       createdband['Captain']['Items'] = []
       createdband['Captain']['Items'].append(capweap)
       createdband['Captain']['Items'].append(capweap2)
       if 'Empty' in createdband['Captain']['Items']:
           createdband['Captain']['Items'].remove('Empty')
           
       
       if 'hasensign' in request.form.keys():
          
           ensspec = request.form['ensspec']
           ensskill = request.form['ensskill']
           ensweap = request.form['ensweap']
           createdband['Ensign'] = dict(app.apprentice['Ensign'])
           createdband['Ensign']['Specialism'] = ensspec
           createdband['Ensign']['Skillset'] = []
           createdband['Ensign']['Skillset'].append(ensskill)
           createdband['Ensign']['Items'] = []
           createdband['Ensign']['Items'].append(ensweap)
           
           if 'Empty' in createdband['Ensign']['Items']:
               createdband['Ensign']['Items'].remove('Empty')
               
       createdband['Troops'] = []
       for item in troops:
           if item != "Empty":
               createdband['Troops'].append(item)
       if len(createdband['Troops']) > 9 :
           return render_template('blankband.html', people=app.troops, wizard=app.wizard, apprentice=app.apprentice, specs = app.specialisms, skills = app.skillsets, weaps = app.weapon, weapcost = app.cost), httpcodes.BAD_REQUEST
       createdband['Treasury'] = int(totalmoney) - sumband(createdband)
       if createdband['Treasury'] < 0:
          return render_template('blankband.html', people=app.troops, wizard=app.wizard, apprentice=app.apprentice, specs = app.specialisms, skills = app.skillsets, weaps = app.weapon, weapcost = app.cost), httpcodes.BAD_REQUEST
       pickle.dump(createdband, open(os.path.join(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser), bandname), "wb"))   
       return render_template('blankband.html', specs = app.specialisms, skills = app.skillsets, people=app.troops, wizard=app.wizard, apprentice=app.apprentice, weapcost = app.cost), httpcodes.CREATED


@app.route('/edit', methods=['GET'])
def edit_warband():
    if os.path.isdir(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser)):
       bands = os.listdir(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser))
    else:
       os.mkdir(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser))
       bands = None
    if request.method == 'GET':
        if app.loggeduser == "":
           return redirect(url_for("welcome_page"))
        else:
           return render_template('bandlist.html', bands=bands, user = app.loggeduser), httpcodes.OK


@app.route('/edit/<band>', methods=['GET','POST'])
def edit_given_warband(band):

    loadedband = pickle.load(open(os.path.join(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser), band), "rb"))
    if request.method == 'GET':
        if app.loggeduser == "":
           return redirect(url_for("welcome_page"))
        else:
           return render_template('editband.html', band=loadedband,  people=app.troops, wizard=app.wizard, apprentice=app.apprentice, specs = app.specialisms, skills = app.skillsets, weaps = app.weapon, weapcost = app.cost), httpcodes.OK
    if request.method == 'POST':
       
       publicstat = request.form['publicstat']
       bandname = request.form['bandname']
       currentmoney = request.form['currentmoney']
       capspec = request.form['capspec']
       #capskill = request.form['capskill']
       skills = json.loads(request.form['capskill'])
       capweap = request.form['capweap']
       capweap2 = request.form['capweap2']
       troops = json.loads(request.form['troops'])
       capmov = request.form['capmove']
       capfig = request.form['capfight']
       capsho = request.form['capshoot']
       capshi = request.form['capshield']
       capmor = request.form['capmorale']
       caphea = request.form['caphealth']
       capexp = request.form['capexperience']
       bought = json.loads(request.form['bought'])
       createdband = dict()
       createdband['public'] = publicstat
       createdband['Name'] = bandname
       
       createdband['Bought'] = bought
       createdband['Captain'] = dict(app.wizard['Captain'])
       createdband['Captain']['Specialism'] = capspec
       createdband['Captain']['Skillset'] = []
       createdband['Captain']['Skillset'].extend(skills)
       createdband['Captain']['Items'] = []
       createdband['Captain']['Items'].append(capweap)
       createdband['Captain']['Items'].append(capweap2)
       
       if 'Empty' in createdband['Captain']['Items']:
           createdband['Captain']['Items'].remove('Empty')
           
       if 'Empty' in createdband['Captain']['Items']:
           createdband['Captain']['Items'].remove('Empty')
           
       createdband['Captain']['Move'] = capmov
       createdband['Captain']['Fight'] = capfig
       createdband['Captain']['Shoot'] = capsho
       createdband['Captain']['Shield'] = capshi
       createdband['Captain']['Morale'] = capmor
       createdband['Captain']['Health'] = caphea
       createdband['Captain']['Experience'] = capexp
       if 'hasensign' in request.form.keys():

           ensspec = request.form['ensspec']
           #ensskill = request.form['ensskill']
           eskills = json.loads(request.form['ensskill'])
           ensmov = request.form['ensmove']
           ensfig = request.form['ensfight']
           enssho = request.form['ensshoot']
           ensshi = request.form['ensshield']
           ensmor = request.form['ensmorale']
           enshea = request.form['enshealth']
           ensexp = request.form['ensexperience']
           ensweap = request.form['ensweap']
           createdband['Ensign'] = dict(app.apprentice['Ensign'])
           createdband['Ensign']['Specialism'] = ensspec
           createdband['Ensign']['Skillset'] = []
           createdband['Ensign']['Skillset'].extend(eskills)
           createdband['Ensign']['Items'] = []
           createdband['Ensign']['Items'].append(ensweap)
           if 'Empty' in createdband['Ensign']['Items']:
               createdband['Ensign']['Items'].remove('Empty')
           createdband['Ensign']['Move'] = ensmov 
           createdband['Ensign']['Fight'] = ensfig
           createdband['Ensign']['Shoot'] = enssho 
           createdband['Ensign']['Shield'] = ensshi 
           createdband['Ensign']['Morale'] = ensmor 
           createdband['Ensign']['Health'] = enshea 
           createdband['Ensign']['Experience'] = ensexp 
       createdband['Troops'] = []
       for item in troops:
           if item != "Empty":
              createdband['Troops'].append(item)
       if len(createdband['Troops']) > 9 :
           return render_template('blankband.html', people=app.troops, wizard=app.wizard, apprentice=app.apprentice, specs = app.specialisms, skills = app.skillsets, weaps = app.weapon, weapcost = app.cost), httpcodes.OK
       
       createdband['Treasury'] = int(currentmoney)
       pickle.dump(createdband, open(os.path.join(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser), bandname), "wb"))  
       return redirect(url_for("edit_warband"))
       

@app.route('/delete/<band>', methods=['GET'])
def delete_given_warband(band):
    os.remove(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands", app.loggeduser), band))
    if os.path.isdir(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser)):
       bands = os.listdir(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser))
    else:
       os.mkdir(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "bands"), app.loggeduser))
       bands = None
    if request.method == 'GET':
       return render_template('bandlist.html', bands=bands), httpcodes.OK


if __name__=="__main__":
    app.run(host='0.0.0.0', port=5000)
