from flask import Flask, render_template, send_file, request, jsonify, session
from rdflib import Graph
from rdflib.namespace import FOAF
import numpy as np
import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace, XSD
from rdflib.namespace import RDF, RDFS
from rdflib import Graph, ConjunctiveGraph, Namespace, Literal
from rdflib.plugins.sparql import prepareQuery
import networkx as nx
import matplotlib.pyplot as plt
from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path  

from rdflib import Graph,URIRef
from gastrodon import LocalEndpoint

import pandas as pd
pd.set_option("display.width",100)
pd.set_option("display.max_colwidth",80)
g = Graph()

filepath = Path('CE_App/static/rdf/out.csv')  
filepathCityA = Path('CE_App/static/rdf/City_A.csv')    
filepathCityB = Path('CE_App/static/rdf/City_B.csv')  

g.namespace_manager.bind('ce', Namespace("https://w3id.org/ce#"), override="False")
ce = Namespace("https://w3id.org/ce#")
app = Flask(__name__)
g.parse("CE_App/static/rdf/SampledKnowledgeGraph.nt")
e=LocalEndpoint(g)
performances=e.select("""
   SELECT  ?City ?Category (count(distinct ?perfs) as ?Total_Performances)
    WHERE {
      { ?events a ce:Event;
      ce:hasCategory ?cat;
      ce:hasSchedule ?sched.}
      {?sched a ce:Schedule;
                ce:hasPerformance ?perfs;
                ce:hasPlace ?places.
                ?places ce:town ?City.
          

       ?cat a ce:Category;
             ce:category ?Category.}
    
     
       }
       GROUP BY  ?City ?Category
       
""")
performances
schedules=e.select("""
   SELECT ?City ?Category (count(distinct ?sched) as ?Total_Schedules)
    WHERE {
      {
      ?events a ce:Event;
                ce:hasCategory ?cat;
                ce:hasSchedule ?sched.
      }
     {
      ?sched a ce:Schedule;
               ce:hasPlace ?place.
      ?place   ce:town ?City.
    
      ?cat a ce:Category;
             ce:category ?Category.
    }
     
       }
       GROUP BY ?City ?Category
       order by Desc(?City)
""")
events=e.select("""
   SELECT ?City ?Category (count(distinct ?events) as ?Total_Events)
    WHERE {
      {
      ?events a ce:Event;
                ce:hasCategory ?cat;
                ce:hasSchedule ?sched.
      }
     {
      ?sched a ce:Schedule;
               ce:hasPlace ?place.
      ?place   ce:town ?City.
    
      ?cat a ce:Category;
             ce:category ?Category.
    }
     
       }
       GROUP BY ?City ?Category
       order by Desc(?City)
""")

df_schedules=schedules.to_html()
df_events=events.to_html()
events= events.reset_index()
schedules=schedules.reset_index()
performances=performances.reset_index()

def month_to_string(month):
        if month == 1 :
            month_string="January"
        elif month == 2:
            month_string="February"
        elif month == 3:
            month_string= "March"
        elif month == 4:
            month_string="April"
        elif month == 5:
            month_string="May"
        elif month == 6:
            month_string="June"
        elif month ==7 :
            month_string="July"
        elif month == 8:
            month_string="August"
        elif month ==9:
            month_string="September"
        elif month == 10:
            month_string="October"
        elif month ==11:
            month_string="November"
        else:
            month_string="December"
        return month_string

@app.route("/TotalEvents",methods=['GET', 'POST'])
def TotalEvents():
      q4 = prepareQuery('''
SELECT (count(distinct ?Events) as ?TotalEvents)

    WHERE {
      ?e ce:event_id ?Events.
      
       }
    
    ''',
  initNs = { "ce": ce}
)     
      events=[]
      for r in g.query(q4):
        events.append(r.TotalEvents)
      q5 = prepareQuery('''
SELECT (count(*) as ?TotalPerformances)

    WHERE {
      ?e a ce:Schedule;
      ce:hasPerformance ?performaces.
      
       }
    
    ''',
  initNs = { "ce": ce}
)
      performances=[]
      for r in g.query(q5):
        performances.append(r.TotalPerformances)
      q3 = prepareQuery('''
SELECT (count(distinct ?Schedule) as ?Total_Schedules)

    WHERE {
      ?e ce:hasSchedule ?Schedule.
      
       }
    
    ''',
  initNs = { "ce": ce}
)
      scheds=[]
      for r in g.query(q3):
        scheds.append(r.Total_Schedules)
    
      q6 = prepareQuery('''
    SELECT (count(distinct ?place) as ?TotalPlaces)

        WHERE {
          ?e ce:hasPlace ?place.
          
          }
        
        ''',
      initNs = { "ce": ce}
    )
      places=[]
      for r in g.query(q6):
        places.append(r.TotalPlaces)
      return events[0],scheds[0],performances[0],places[0]
        
import plotly.express as px

def plot_ScheduleFrequency_byCategory_ofCity(properties,city):
  St=properties[properties['City']==city]
  St
  fig=px.bar(St, x='Category', y='Total_Schedules',title="Schedule Frequency by category of "+city,labels={'Category': "Category",'Total_Schedules':'Frequency'})
  return fig.to_json(),St 

def plot_EventFrequency_byCategory_ofCity(properties,city):
      St=properties[properties['City']==city]
      St
      fig=px.bar(St, x='Category', y='Total_Events',title="Event Frequency by category of "+city,labels={'Category': "Category",'Total_Events':'Frequency'})
      return fig.to_json(),St
    
def plot_PerformanceFrequency_byCategory_ofCity(properties,city):
      St=properties[properties['City']==city]
      St
      fig=px.bar(St, x='Category', y='Total_Performances',title="Performance Frequency by category of "+city,labels={'Category': "Category",'Total_Events':'Frequency'})
      return fig.to_json(),St
    
@app.route("/my_data/",methods=['GET', 'POST'])
def my_data():
      if(request.form.get('city')== None):
            return render_template("pandas.html",schedules=df_schedules,CityList=cities(schedules))
      else:
            cityData= schedules[schedules['City']==request.form.get('city')]
            return render_template("pandas.html",schedules=cityData.to_html(),CityList=cities(schedules))
from plotly.subplots import make_subplots
import plotly.graph_objects as go

category=e.select("""
   SELECT  ?category (count(?sched) as ?Total_Schedules)
    WHERE {
      {
      ?events a ce:Event;
                ce:hasCategory ?cat;
                ce:hasSchedule ?sched.
      }
     {
      
    
      ?cat a ce:Category;
             ce:category ?category.
    }
     
       }
       GROUP BY ?category
""")

category=category.reset_index()    
  
eventCategory=e.select("""
   SELECT  ?category (count(distinct ?events) as ?Total_Events)
    WHERE {
      {
      ?events a ce:Event;
                ce:hasCategory ?cat;
                ce:hasSchedule ?sched.
      }
     {
      
    
      ?cat a ce:Category;
             ce:category ?category.
    }
     
       }
       GROUP BY ?category
""")
performancesLoc=e.select("""
   SELECT  ?long ?lat ?id ?Town ?Name  ?Place_Name (count(distinct ?perfs) as ?Total_Performances)
    WHERE {
      { ?events a ce:Event;
      ce:event_id ?id;
      ce:name ?Name;
      ce:hasSchedule ?sched.
      }
      {
        ?sched a ce:Schedule;
                ce:hasPerformance ?perfs;
                ce:hasPlace ?places.
      ?places ce:town ?Town;
      ce:name ?Place_Name;
      
           ce:hasLocation ?loc.
          ?loc ce:latitude ?lat;
          ce:longitude ?long.

        }
       }
       GROUP BY  ?long ?lat ?id ?Name ?Place_Name
       
""")
performanceCategory=e.select("""
   SELECT   ?Category (count(distinct ?perfs) as ?Total_Performances)
    WHERE {
      { ?events a ce:Event;
      ce:hasCategory ?cat;
      ce:hasSchedule ?sched.}
      {?sched a ce:Schedule;
                ce:hasPerformance ?perfs;
                ce:hasPlace ?places.
                ?places ce:town ?City.
          

       ?cat a ce:Category;
             ce:category ?Category.}
    
     
       }
       GROUP BY   ?Category
       
""")

category=category.reset_index()

eventCategory =eventCategory.reset_index()

performanceCategory= performanceCategory.reset_index()

@app.route("/VisualseCatFreq",methods=['GET', 'POST'])   
def VisualseCatFreq():
      
      fig=px.bar(category,x='category',y='Total_Schedules',title='Overall Category Frequencies')
      print(category)
      return render_template("ScheduleVizHomePage.html",plo_=fig.to_json())
    
@app.route("/VisualseEventCatFreq",methods=['GET', 'POST'])   
def VisualseEventCatFreq():
      
      fig=px.bar(eventCategory,x='category',y='Total_Events',title='Overall Category Frequencies')
      print(category)
      return render_template("EventVizHomePage.html",plo_=fig.to_json())
    
@app.route("/VisualsePerformanceCatFreq",methods=['GET', 'POST'])   
def VisualsePerformanceCatFreq():
      
      fig=px.bar(performanceCategory,x='Category',y='Total_Performances',title='Overall Category Frequencies')
      print(category)
      return render_template("PerformanceVizHomePage.html",plo_=fig.to_json())

@app.route("/plot_comparison/",methods=['GET', 'POST'])
def plot_comparison():
      if(request.form.get('city A')== None):
            cityA= "St Andrews"
      else:
            cityA= request.form.get('city A')
      if(request.form.get('city B')== None):
            cityB= "Edinburgh"
      else:
            cityB= request.form.get('city B')
      City_1=schedules[schedules['City']==cityA]
      City_1
      City_2=schedules[schedules['City']==cityB]
      City_2
      fig = go.Figure()
      fig.add_trace(go.Bar(x=City_1["Category"], y=City_1["Total_Schedules"], name=City_1['City'].iloc[0],
            hovertemplate="City: %s<br>Event Type: %%{x}<br>Schedules = %%{y}<extra></extra>"% City_1['City'].iloc[0]))
      fig.add_trace(go.Bar(x=City_2["Category"], y=City_2["Total_Schedules"], name=City_2['City'].iloc[0],
            hovertemplate="City: %s<br>Event Type: %%{x}<br>Schedules = %%{y}<extra></extra>"% City_2['City'].iloc[0]))
      fig.update_layout(title_text= "Category wise comparison of Schedules of "+cityA+" and "+cityB)
      fig.update_layout(legend_title_text= "Category")
      fig.update_xaxes(title_text='Category')
      fig.update_yaxes(title_text='Schedule Frequency')
      City_1.to_csv(filepathCityA)
      City_2.to_csv(filepathCityB)
      return render_template("CityComparison.html",
                           plot_=fig.to_json(),CityList=cities(schedules),City_A=City_1.to_html(),City_B=City_2.to_html(),dataCity_A=cityA,dataCity_B=cityB)           
  
@app.route("/plot_eventComparison/",methods=['GET', 'POST'])
def plot_eventComparison():
      if(request.form.get('city A')== None):
            cityA= "St Andrews"
      else:
            cityA= request.form.get('city A')
      if(request.form.get('city B')== None):
            cityB= "Edinburgh"
      else:
            cityB= request.form.get('city B')
      City_1=events[events['City']==cityA]
      City_1
      City_2=events[events['City']==cityB]
      City_2
      fig = go.Figure()
      fig.add_trace(go.Bar(x=City_1["Category"], y=City_1["Total_Events"], name=City_1['City'].iloc[0],
            hovertemplate="City: %s<br>Event Type: %%{x}<br>Events = %%{y}<extra></extra>"% City_1['City'].iloc[0]))
      fig.add_trace(go.Bar(x=City_2["Category"], y=City_2["Total_Events"], name=City_2['City'].iloc[0],
            hovertemplate="City: %s<br>Event Type: %%{x}<br>Events = %%{y}<extra></extra>"% City_2['City'].iloc[0]))
      fig.update_layout(title_text= "Category wise comparison of Events of "+cityA+" and "+cityB)
      fig.update_layout(legend_title_text= "Category")
      fig.update_xaxes(title_text='Category')
      fig.update_yaxes(title_text='Events Frequency')
      City_1.to_csv(filepathCityA)
      City_2.to_csv(filepathCityB)
      return render_template("EventCityComparison.html",
                           plot_=fig.to_json(),CityList=cities(schedules),City_A=City_1.to_html(),City_B=City_2.to_html(),dataCity_A=cityA,dataCity_B=cityB)           
  
@app.route("/plot_performanceComparison/",methods=['GET', 'POST'])
def plot_performanceComparison():
      if(request.form.get('city A')== None):
            cityA= "St Andrews"
      else:
            cityA= request.form.get('city A')
      if(request.form.get('city B')== None):
            cityB= "Edinburgh"
      else:
            cityB= request.form.get('city B')
      City_1=performances[performances['City']==cityA]
      City_1
      City_2=performances[performances['City']==cityB]
      City_2
      fig = go.Figure()
      fig.add_trace(go.Bar(x=City_1["Category"], y=City_1["Total_Performances"], name=City_1['City'].iloc[0],
            hovertemplate="City: %s<br>Event Type: %%{x}<br>Performances = %%{y}<extra></extra>"% City_1['City'].iloc[0]))
      fig.add_trace(go.Bar(x=City_2["Category"], y=City_2["Total_Performances"], name=City_2['City'].iloc[0],
            hovertemplate="City: %s<br>Event Type: %%{x}<br>Performances = %%{y}<extra></extra>"% City_2['City'].iloc[0]))
      fig.update_layout(title_text= "Category wise comparison of Performances of "+cityA+" and "+cityB)
      fig.update_layout(legend_title_text= "Category")
      fig.update_xaxes(title_text='Category')
      fig.update_yaxes(title_text='Performances Frequency')
      City_1.to_csv(filepathCityA)
      City_2.to_csv(filepathCityB)
      return render_template("PerformancesCityComparison.html",
                           plot_=fig.to_json(),CityList=cities(schedules),City_A=City_1.to_html(),City_B=City_2.to_html(),dataCity_A=cityA,dataCity_B=cityB)           
  
def cities(schedules):
      mylist=pd.unique(schedules['City'])
      return mylist


@app.route("/")
def home_page():
    events,scheds, performances,places=TotalEvents()
    return render_template("base.html",TotalEvents=events, Total_Schedules=scheds, TotalPerformances=performances,TotalPlaces=places )

@app.route("/VisuliseScheduleCatgory",methods=['GET', 'POST'])
def VisuliseScheduleCatgory():
      if(request.form.get('city')== None or request.form.get('city')=="None"):
            city= "St Andrews"
      else:
            city= request.form.get('city')
            
      plot_,City_data=plot_ScheduleFrequency_byCategory_ofCity(schedules,city)
      City_data.to_csv(filepath)
      return render_template("City_Cat_Freq.html",
                          plot_=plot_,City_data=City_data.to_html() ,CityList=cities(schedules),city=city)
@app.route("/VisuliseEventCatgory",methods=['GET', 'POST'])
def VisuliseEventCatgory():
      if(request.form.get('city')== None or request.form.get('city')=="None"):
            city= "St Andrews"
      else:
            city= request.form.get('city')
            
      plot_,City_data=plot_EventFrequency_byCategory_ofCity(events,city)
      City_data.to_csv(filepath)
      return render_template("EventCity_Cat_Freq.html",
                          plot_=plot_,City_data=City_data.to_html() ,CityList=cities(schedules),city=city)
@app.route("/VisulisePerformancesCatgory",methods=['GET', 'POST'])
def VisulisePerformancesCatgory():
      if(request.form.get('city')== None or request.form.get('city')=="None"):
            city= "St Andrews"
      else:
            city= request.form.get('city')
            
      plot_,City_data=plot_PerformanceFrequency_byCategory_ofCity(performances,city)
      City_data.to_csv(filepath)
      
      return render_template("PerformanceCity_Cat_Freq.html",
                          plot_=plot_,City_data=City_data.to_html() ,CityList=cities(schedules),city=city)
@app.route("/ScheduleMap",methods=['GET', 'POST'])      
def ScheduleMap():
      if(request.form.get('city')==None or request.form.get('city')=="None"):
            locations=e.select('''
SELECT ?lat ?long ?id ?Name ?Place_Name (count (?schedules )as ?Schedule_Frequency) 

    WHERE {
      {

       ?events ce:event_id ?id;
       ce:name ?Name;
       ce:hasSchedule ?schedules.
       ?schedules a ce:Schedule;
       ce:hasPlace ?place.
       }  
  {
    ?place a ce:Place;
        ce:town ?Town;
        ce:name ?Place_Name;
        
        ce:hasLocation ?loc.
      ?loc  ce:latitude ?lat;
        ce:longitude ?long.    
  }
    }
       group by ?lat ?long ?id ?Name ?Place_Name
       order by desc (?Schedule_Frequency) 
    ''',
  initNs = { "ce": ce}
)     
            locations= locations.reset_index()
            fig = px.scatter_mapbox(locations, lat="lat", lon="long", hover_name="Name", hover_data=["Place_Name","id", "Schedule_Frequency"],
                        size='Schedule_Frequency',color_discrete_sequence=["red"], zoom=3, height=500)
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            return render_template("schedule_map.html",plot_=fig.to_json(),cityList=cities(schedules))
      else:   
        city=request.form.get('city')
        locations=e.select('''
  SELECT   ?lat ?long ?id ?Name ?Place_Name (count (?schedules )as ?Schedule_Frequency) 

      WHERE {
        {

        ?events ce:event_id ?id;
        ce:name ?Name;
        ce:hasSchedule ?schedules.
        ?schedules a ce:Schedule;
        ce:hasPlace ?place.
        }
        
    {
      ?place a ce:Place;
          ce:town ?Town;
          ce:name ?Place_Name;
          
          ce:hasLocation ?loc.
        ?loc  ce:latitude ?lat;
          ce:longitude ?long.
          

    }
    filter(?Town="%s")
        
        
        }
        
        group by ?lat ?long ?id ?Name ?Place_Name
        order by desc (?Schedule_Frequency)

      '''%city,
    initNs = { "ce": ce}
  ) 
        locations= locations.reset_index()
        fig = px.scatter_mapbox(locations, lat="lat", lon="long", hover_name="Name", hover_data=["Place_Name","id", "Schedule_Frequency"],
                         size='Schedule_Frequency',color_discrete_sequence=["red"], zoom=3, height=500)
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return render_template("schedule_map.html",plot_=fig.to_json(),cityList=cities(schedules))


@app.route("/EventMap",methods=['GET', 'POST'])      
def EventMap():
      if(request.form.get('city')==None or request.form.get('city')=="None"):
            locations=e.select('''
SELECT  ?lat ?long ?id ?Name ?Place_Name (count (?events )as ?Event_Frequency) 

    WHERE {
      {

       ?events ce:event_id ?id;
       ce:name ?Name;
       ce:hasSchedule ?schedules.
       ?schedules a ce:Schedule;
       ce:hasPlace ?place.
       }
       
  {
    ?place a ce:Place;
    
        ce:town ?Town;
        ce:name ?Place_Name;
        ce:hasLocation ?loc.
      ?loc  ce:latitude ?lat;
        ce:longitude ?long.
      
  }
 
       }
       
       group by ?lat ?long ?id ?Name ?Place_Name
      
    ''',
  initNs = { "ce": ce}
)     
            locations= locations.reset_index()
            fig = px.scatter_mapbox(locations, lat="lat", lon="long", hover_name="Name", hover_data=["Place_Name","id", "Event_Frequency"],
                        size='Event_Frequency',color_discrete_sequence=["red"], zoom=3, height=500, title="Event Map")
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            return render_template("event_map.html",plot_=fig.to_json(),cityList=cities(schedules))
      else:   
        city=request.form.get('city')
        locations=e.select('''
  SELECT  ?lat ?long ?id ?Name ?Place_Name (count (?events )as ?Event_Frequency) 

      WHERE {
        {

        ?events ce:event_id ?id;
        ce:name ?Name;
        ce:hasSchedule ?schedules.
        ?schedules a ce:Schedule;
        ce:hasPlace ?place.
        }
        
    {
      ?place a ce:Place;
          ce:town ?Town;
          ce:name ?Place_Name;
          ce:hasLocation ?loc.
          filter(?Town="%s")
        ?loc  ce:latitude ?lat;
          ce:longitude ?long.
          

    }
    
        
        
        }
        
        group by ?lat ?long ?id ?Name ?Place_Name
        
      '''%city,
    initNs = { "ce": ce}
  ) 
        locations= locations.reset_index()
        fig = px.scatter_mapbox(locations, lat="lat", lon="long", hover_name="Name", hover_data=["Place_Name","id", "Event_Frequency"],
                        size='Event_Frequency',color_discrete_sequence=["red"], zoom=3, height=500, title="Event Map for "+city)
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return render_template("event_map.html",plot_=fig.to_json(),cityList=cities(schedules))

@app.route("/PerformanceMap",methods=['GET', 'POST'])  
def PerformanceMap():
      locations=performancesLoc
      locations= locations.reset_index()
      if(request.form.get('city')==None or request.form.get('city')=="None"):
           
            
            fig = px.scatter_mapbox(locations, title="Performance Map", lat="lat", lon="long", hover_name="Name", hover_data=["Place_Name","id", "Total_Performances"],
                        size= 'Total_Performances',color_discrete_sequence=["red"], zoom=3, height=500)
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            return render_template("performance_map.html",plot_=fig.to_json(),cityList=cities(schedules))
      else:   
        city=request.form.get('city')
        
        locations= locations[locations['Town']==city]
        fig = px.scatter_mapbox(locations, title="Performance Map for "+city, lat="lat", lon="long", hover_name="Name", hover_data=["Place_Name","id", "Total_Performances"],
                        size= 'Total_Performances', color_discrete_sequence=["red"], zoom=3, height=500)
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return render_template("performance_map.html",plot_=fig.to_json(),cityList=cities(schedules))
@app.route("/scheduleHist",methods=['GET', 'POST'])  
def scheduleHist():
      if(request.form.get('city')==None or request.form.get('city')=="None"):
            
        q8 = e.select('''
  SELECT  (Month(?Date) as ?month) (year(?Date) as ?year) (count(?sched) as ?Total_Schedules) 

      WHERE {
        {?events a ce:Event;
        ce:hasCategory ?cat;
        ce:hasSchedule ?sched.}
      { 
        ?sched a ce:Schedule;
          ce:start_ts ?Date;
          ce:hasPlace ?place.
        ?place ce:town ?Town.
        ?cat a ce:Category;
      ce:category ?cats.}
      
        
        }
        group by ?Date
        
      ''')
        
        q8=q8.reset_index()
        q8=q8.sort_values(by=['year','month'])
        q8['month']=q8['month'].apply(month_to_string)
        q8['date']=q8['month'].astype(str)+' '+q8['year'].astype(str)
        q8.to_csv(filepath)
        fig=px.histogram(q8,x='date',y='Total_Schedules', hover_data=["month","year" ,"Total_Schedules"],title='Schedule Histogram')
        return render_template("scheduleHist.html",plot_=fig.to_json(),cityList=cities(schedules))
      else:
            
            
            city=request.form.get('city')
            q8 = e.select('''
SELECT  ?Town (Month(?Date) as ?month) (year(?Date) as ?year) (count(?sched) as ?Total_Schedules) 

    WHERE {
      {?events a ce:Event;
      ce:hasCategory ?cat;
      ce:hasSchedule ?sched.}
     { 
       ?sched a ce:Schedule;
        ce:start_ts ?Date;
         
        ce:hasPlace ?place.
        filter (?Town= "%s")
      ?place ce:town ?Town.
      ?cat a ce:Category;
    ce:category ?cats.}
   
    
      
       }
       group by ?Date 
       order by desc(?Date)
    
    '''%city, initNs = { "ce": ce})
            q8=q8.reset_index()
            q8=q8.sort_values(by=['year','month'])
            q8['month']=q8['month'].apply(month_to_string)
            q8['date']=q8['month'].astype(str)+'-'+q8['year'].astype(str)
            q8.to_csv(filepath)
            fig=px.histogram(q8,x='date',y='Total_Schedules',hover_name="Town", hover_data=["Town","month","year" ,"Total_Schedules"],title='Schedule Histogram for '+city)
            return render_template("scheduleHist.html",plot_=fig.to_json(),cityList=cities(schedules))
@app.route("/performanceHist",methods=['GET', 'POST'])  
def performanceHist():
      if(request.form.get('city')==None or request.form.get('city')=="None"):
            
        q8 = e.select('''
  SELECT   (Month(?Date) as ?month) (year(?Date) as ?year) (count(?perfs) as ?Total_Performances) 

      WHERE {
        {?events a ce:Event;
        ce:hasCategory ?cat;
        ce:hasSchedule ?sched.}
      { 
        ?sched a ce:Schedule;
          ce:start_ts ?Date;
          ce:hasPerformance ?perfs;
          ce:hasPlace ?place.
        ?place ce:town ?Town.
        ?cat a ce:Category;
      ce:category ?cats.}
      
        }
        group by ?Date
        
  
      ''')
        
        q8=q8.reset_index()
        q8=q8.sort_values(by=['year','month'])
        q8['month']=q8['month'].apply(month_to_string)
        q8['date']=q8['month'].astype(str)+' '+q8['year'].astype(str)
        q8.to_csv(filepath)
        fig=px.histogram(q8,x='date',y='Total_Performances', hover_data=["month","year" ,"Total_Performances"],title='Performance Histogram')
        fig.update_yaxes( range=[0,5000],  # sets the range of xaxis
    constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
)
        return render_template("performanceHist.html",plot_=fig.to_json(),cityList=cities(schedules))
      else:
            
            
            city=request.form.get('city')
            q8 = e.select('''
SELECT  ?Town (Month(?Date) as ?month) (year(?Date) as ?year) (count(?perfs) as ?Total_Performances) 

    WHERE {
      {?events a ce:Event;
      ce:hasCategory ?cat;
      ce:hasSchedule ?sched.}
     { 
       ?sched a ce:Schedule;
        ce:start_ts ?Date;
         ce:hasPerformance ?perfs;
        ce:hasPlace ?place.
      ?place ce:town ?Town.
       filter (?Town= "%s")
      ?cat a ce:Category;
    ce:category ?cats.}
   
   
       }
       group by ?Date
       order by desc(?Date)

    '''%city, initNs = { "ce": ce})
            q8=q8.reset_index()
            q8=q8.sort_values(by=['year','month'])
            q8['month']=q8['month'].apply(month_to_string)
            q8['date']=q8['month'].astype(str)+'-'+q8['year'].astype(str)
            q8.to_csv(filepath)
            fig=px.histogram(q8,x='date',y='Total_Performances',hover_name="Town", hover_data=["Town","month","year" ,"Total_Performances"],title='Performance Histogram for '+city)
            
            return render_template("performanceHist.html",plot_=fig.to_json(),cityList=cities(schedules))
          
@app.route("/eventHist",methods=['GET', 'POST'])  
def eventHist():
      if(request.form.get('city')==None or request.form.get('city')=="None"):
            
        q8 = e.select('''
  SELECT  (Month(?Date) as ?month) (year(?Date) as ?year) (count(distinct ?events) as ?Total_Events) 

      WHERE {
        {?events a ce:Event;
        ce:hasCategory ?cat;
        ce:hasSchedule ?sched.}
      { 
        ?sched a ce:Schedule;
          ce:start_ts ?Date;
          ce:hasPlace ?place.
        ?place ce:town ?Town.
        ?cat a ce:Category;
      ce:category ?cats.}
      
        
        }
        group by ?Date

      ''')
        
        q8=q8.reset_index()
        q8=q8.sort_values(by=['year','month'])
        q8['month']=q8['month'].apply(month_to_string)
        q8['date']=q8['month'].astype(str)+' '+q8['year'].astype(str)
        q8.to_csv(filepath)
        fig=px.histogram(q8,x='date',y='Total_Events', hover_data=["month","year" ,"Total_Events"],title='Event Histogram')
        return render_template("eventHist.html",plot_=fig.to_json(),cityList=cities(schedules))
      else:
            
            
            city=request.form.get('city')
            q8 = e.select('''
SELECT  ?Town (Month(?Date) as ?month) (year(?Date) as ?year) (count(distinct ?events) as ?Total_Events) 

    WHERE {
      {?events a ce:Event;
      ce:hasCategory ?cat;
      ce:hasSchedule ?sched.}
     { 
       ?sched a ce:Schedule;
        ce:start_ts ?Date;
        ce:hasPlace ?place.
      ?place ce:town ?Town.
       filter (?Town= "%s")
      ?cat a ce:Category;
    ce:category ?cats.}
   
    
      
       }
       group by ?Date
       order by desc(?Date)
 
    '''%city, initNs = { "ce": ce})
            q8=q8.reset_index()
            q8=q8.sort_values(by=['year','month'])
            q8['month']=q8['month'].apply(month_to_string)
            q8['date']=q8['month'].astype(str)+'-'+q8['year'].astype(str)
            q8.to_csv(filepath)
            fig=px.histogram(q8,x='date',y='Total_Events',hover_name="Town", hover_data=["Town","month","year" ,"Total_Events"],title='Event Histogram for '+city)
            return render_template("eventHist.html",plot_=fig.to_json(),cityList=cities(schedules))
 
@app.route("/dateData",methods=['GET', 'POST'])      
def dateData():
      if (request.form.get('from')==None and request.form.get('to')==None ):
            startYear="2017"
            endYear="2022"
      elif(request.form.get('from')==None):
            startYear=request.form.get('to')
            endYear= request.form.get('to')
      elif(request.form.get('to')==None):
            startYear=request.form.get('from')
            endYear= request.form.get('from')
      elif(request.form.get('from')>request.form.get('to')):
            startYear= request.form.get('to')
            endYear= request.form.get('from')
      else:
        startYear=request.form.get('from')
        endYear= request.form.get('to')
      if(startYear==endYear):
            start= startYear+"-01-01T10:20:13+05:30"
            end= startYear+"-12-31T10:20:13+05:30"
      else:
            start= startYear+"-01-01T10:20:13+05:30"
            end=endYear+"-01-01T10:20:13+05:30"
      dateData=e.select('''
SELECT ?Town (count(?sched) as ?Total_Schedules) 

    WHERE {
      {?events a ce:Event;
      ce:hasCategory ?cat;
      ce:hasSchedule ?sched.}
    { 
      ?sched a ce:Schedule;
        ce:start_ts ?Date;
          
        ce:hasPlace ?place.
        FILTER (?Date >"%s"^^xsd:dateTime)
      FILTER (?Date < "%s"^^xsd:dateTime)
      ?place ce:town ?Town.
      ?cat a ce:Category;
    ce:category ?cats.}   
  
  
      }
Group by ?Town 

    '''%(start,end),
  initNs = { "ce": ce}
)
      dateDataR=dateData.reset_index()
      if(request.form.get('city')==None or request.form.get('city')=="None"):
            dateDataR.to_csv(filepath)
            if(startYear==endYear):
                  fig=px.bar(dateDataR,x='Town',y='Total_Schedules',title='Schedule Frequency Viz for '+startYear)
            else:
              fig=px.bar(dateDataR,x='Town',y='Total_Schedules',title='Schedule Frequency Viz for '+startYear +' to '+ endYear) 
            return render_template("dateData.html",year1=startYear,year2=endYear, plot_=fig.to_json(),dateData=dateData.to_html(),cityList=cities(schedules))
                  
              
      else:
            
            dateDataR=dateDataR[dateDataR['Town']==request.form.get('city')]
            dateDataR.to_csv(filepath)
            if(startYear==endYear):
                  fig=px.bar(dateDataR,x='Town',y='Total_Schedules',title='Schedule Frequency Viz for '+request.form.get('city')+" "+startYear)
            else:
                  fig=px.bar(dateDataR,x='Town',y='Total_Schedules',title='Schedule Frequency Viz for ' +request.form.get('city')+" "+ startYear + " to "+ endYear) 
            return render_template("dateData.html",year1=startYear,year2=endYear, plot_=fig.to_json(),dateData=dateDataR.to_html(),cityList=cities(schedules))
            
            
@app.route("/eventDateData",methods=['GET', 'POST'])      
def eventDateData():
      if (request.form.get('from')==None and request.form.get('to')==None ):
            startYear="2017"
            endYear="2022"
      elif(request.form.get('from')==None):
            startYear=request.form.get('to')
            endYear= request.form.get('to')
      elif(request.form.get('to')==None):
            startYear=request.form.get('from')
            endYear= request.form.get('from')
      elif(request.form.get('from')>request.form.get('to')):
            startYear= request.form.get('to')
            endYear= request.form.get('from')
      else:
        startYear=request.form.get('from')
        endYear= request.form.get('to')
      if(startYear==endYear):
            start= startYear+"-01-01T10:20:13+05:30"
            end= startYear+"-12-31T10:20:13+05:30"
      else:
            start= startYear+"-01-01T10:20:13+05:30"
            end=endYear+"-01-01T10:20:13+05:30"
      dateData=e.select('''
SELECT ?Town (count(distinct ?events) as ?Total_Events) 

    WHERE {
      {?events a ce:Event;
      ce:hasCategory ?cat;
      ce:hasSchedule ?sched.}
    { 
      ?sched a ce:Schedule;
        ce:start_ts ?Date;
        
        ce:hasPlace ?place.
         FILTER (?Date >"%s"^^xsd:dateTime)
      FILTER (?Date < "%s"^^xsd:dateTime) 
      ?place ce:town ?Town.
      ?cat a ce:Category;
    ce:category ?cats.}
    
      
      }
Group by ?Town 

    '''%(start,end),
  initNs = { "ce": ce}
)
      dateDataR=dateData.reset_index()
      if(request.form.get('city')==None or request.form.get('city')=="None"):
            dateDataR.to_csv(filepath)
            if(startYear==endYear):
                  fig=px.bar(dateDataR,x='Town',y='Total_Events',title='Events Frequency Viz for '+startYear)
            else:
              fig=px.bar(dateDataR,x='Town',y='Total_Events',title='Events Frequency Viz for '+startYear +' to '+ endYear) 
            return render_template("event_dateData.html",year1=startYear,year2=endYear, plot_=fig.to_json(),dateData=dateData.to_html(),cityList=cities(schedules))
                          
      else:
            dateDataR=dateDataR[dateDataR['Town']==request.form.get('city')]
            dateDataR.to_csv(filepath)
            if(startYear==endYear):
                  fig=px.bar(dateDataR,x='Town',y='Total_Events',title='Events Frequency Viz for '+request.form.get('city')+" "+startYear)
            else:
                  fig=px.bar(dateDataR,x='Town',y='Total_Events',title='Events Frequency Viz for ' +request.form.get('city')+" "+ startYear + " to "+ endYear) 
            return render_template("event_dateData.html",year1=startYear,year2=endYear, plot_=fig.to_json(),dateData=dateDataR.to_html(),cityList=cities(schedules))
@app.route("/performanceDateData",methods=['GET', 'POST'])      
def performanceDateData():
      if (request.form.get('from')==None and request.form.get('to')==None ):
            startYear="2017"
            endYear="2022"
      elif(request.form.get('from')==None):
            startYear=request.form.get('to')
            endYear= request.form.get('to')
      elif(request.form.get('to')==None):
            startYear=request.form.get('from')
            endYear= request.form.get('from')
      elif(request.form.get('from')>request.form.get('to')):
            startYear= request.form.get('to')
            endYear= request.form.get('from')
      else:
        startYear=request.form.get('from')
        endYear= request.form.get('to')
      if(startYear==endYear):
            start= startYear+"-01-01T10:20:13+05:30"
            end= startYear+"-12-31T10:20:13+05:30"
      else:
            start= startYear+"-01-01T10:20:13+05:30"
            end=endYear+"-01-01T10:20:13+05:30"
      dateData=e.select('''
SELECT ?Town (count(distinct ?perfs) as ?Total_Performances) 

    WHERE {
      {?events a ce:Event;
      ce:hasCategory ?cat;
      ce:hasSchedule ?sched.}
    { 
      ?sched a ce:Schedule;
        ce:start_ts ?Date;
       
        ce:hasPlace ?place;
        ce:hasPerformance ?perfs.
         FILTER (?Date >"%s"^^xsd:dateTime)
      FILTER (?Date < "%s"^^xsd:dateTime)
      ?place ce:town ?Town.
      ?cat a ce:Category;
    ce:category ?cats.}
    
         
      }
Group by ?Town 
    '''%(start,end),
  initNs = { "ce": ce}
)
      dateDataR=dateData.reset_index()
      print(request.form.get('city'))
      if(request.form.get('city')==None or request.form.get('city')=="None"):
            dateDataR.to_csv(filepath)
            if(startYear==endYear):
                  fig=px.bar(dateDataR,x='Town',y='Total_Performances',title='Performance Frequency Viz for '+startYear)
            else:
                  fig=px.bar(dateDataR,x='Town',y='Total_Performances',title='Performance Frequency Viz for '+startYear +' to '+ endYear) 
            fig.update_yaxes( range=[0,2000],  # sets the range of xaxis
    constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
)
            return render_template("performance_dateData.html",year1=startYear,year2=endYear, plot_=fig.to_json(),dateData=dateData.to_html(),cityList=cities(schedules))
            
      else:
            
            dateDataR=dateDataR[dateDataR['Town']==request.form.get('city')]
            dateDataR.to_csv(filepath)
            if(startYear==endYear):
                  fig=px.bar(dateDataR,x='Town',y='Total_Performances',title='Performance Frequency Viz for '+request.form.get('city')+" "+startYear)
            else:
                  fig=px.bar(dateDataR,x='Town',y='Total_Performances',title='Performance Frequency Viz for ' +request.form.get('city')+" "+ startYear + " to "+ endYear) 
            fig.update_yaxes( range=[0,2000],  # sets the range of xaxis
    constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
)
            return render_template("performance_dateData.html",year1=startYear,year2=endYear, plot_=fig.to_json(),dateData=dateDataR.to_html(),cityList=cities(schedules))
                
                    