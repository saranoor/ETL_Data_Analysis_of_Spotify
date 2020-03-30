# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 15:31:15 2020

@author: saran
"""
import pandas as pd
#import matplotlib.pyplot as plt
import os         
from sqlalchemy import create_engine
import sqlalchemy.types
import spotipy
import spotipy.util as util
import seaborn as sns
os.environ['SPOTIPY_CLIENT_ID'] = '00b7317977ad4c0d971af8274f1aa790'
os.environ['SPOTIPY_CLIENT_SECRET'] = '6efbf45fe72d435f9739d0c0f4c26db5'
os.environ['SPOTIPY_REDIRECT_URI'] = 'https://360i.com/'
base_url = 'https://api.spotify.com'
scope = 'playlist-read-private'
# spotify:playlist:
rap_caviar = '37i9dQZF1DX0XUsuxWHRQd'
engine = create_engine('sqlite:///playlist_RC.db', echo=False)
conn=engine.connect()
token = util.prompt_for_user_token('Puffer Fish',scope=scope)
sp = spotipy.Spotify(auth=token)
playlists = sp.user_playlists('spotify')
df_tracks = pd.DataFrame(columns=['name', 'popularity', 'duration_ms', 'artist_name'])
df_artists = pd.DataFrame(columns=['id', 'a_name', 'a_popularity', 'followers','tracks'])
for playlist in playlists['items']:

            if rap_caviar in playlist['id']:
                print('total songs:', playlist['name'],'are', playlist['tracks']['total'])
                tracks=sp.playlist_tracks(playlist['id'],fields='items.track.name, items.track.artists, items.track.duration_ms,items.track.popularity', offset=0, market=None)

                count=0
                t=0
                for i in range(0,len(tracks['items'])):
                    try:
                        track_name=tracks['items'][i]['track']['name']
                    except:
                        track_name=''
                    try:
                        track_durations=tracks['items'][i]['track']['duration_ms']
                    except:
                        track_durations=''
                    try:
                        track_popularity=tracks['items'][i]['track']['popularity']
                    except:
                        track_popularity=''
                    try:    
                        tract_artist=tracks['items'][i]['track']['artists'][0]['name']
                    except:
                        track_artist=''
                    #df_tracks.loc[i]=[tracks['items'][i]['track']['name'],tracks['items'][i]['track']['duration_ms'],tracks['items'][i]['track']['popularity'],tracks['items'][i]['track']['artists'][0]['name']]
                    df_tracks.loc[i]=[track_name,track_popularity,track_durations,tract_artist]
                    count=count+1
                    for j in range(0, len(tracks['items'][i]['track']['artists'])):
                        try:
                            artist = sp.artist(tracks['items'][i]['track']['artists'][j]['uri'])
                            df_artists.loc[t,'a_name']=tracks['items'][i]['track']['artists'][j]['name']
                            df_artists.loc[t,'id']=tracks['items'][i]['track']['artists'][j]['id']
                            df_artists.loc[t,'tracks']=tracks['items'][i]['track']['name']
                            try:
                                df_artists.loc[t,'a_popularity']=artist['popularity']
                            except:
                                df_artists.loc[t,'a_popularity']=''
                            try:
                                df_artists.loc[t,'followers']=artist['followers']['total']
                            except:
                                df_artists.loc[t,'followers']=''
                                #df_artists.loc[t]=[tracks['items'][i]['track']['artists'][j]['id'],tracks['items'][i]['track']['artists'][j]['name'],artist['followers']['total'],artist['popularity']]
                            t=t+1
                        except:
                            df_artists.loc[t,'a_name']=tracks['items'][i]['track']['artists'][j]['name']
                            df_artists.loc[t,'id']=tracks['items'][i]['track']['artists'][j]['id']
                            df_artists.loc[t,'tracks']=tracks['items'][i]['track']['name']
                            #df_artists.loc[t]=[tracks['items'][i]['track']['artists'][j]['id'],tracks['items'][i]['track']['artists'][j]['name'],'','']
                            t=t+1
                            
                            pass
                        


df_tracks.to_sql('tracks_database', con=engine, index=False, if_exists='replace',
                 dtype={"name":sqlalchemy.types.NVARCHAR(length=255), 
                        "popularity":sqlalchemy.types.Integer(),
                        "duration_ms":sqlalchemy.types.Integer(), 
                        "artist_name":sqlalchemy.types.NVARCHAR(length=255)})
   
df_artists.to_sql('artists_database', con=engine, index=False, if_exists='replace',
                 dtype={"id":sqlalchemy.types.NVARCHAR(length=255), 
                        "a_name":sqlalchemy.types.NVARCHAR(length=255),
                        "a_popularity":sqlalchemy.types.Integer(),
                        "followers":sqlalchemy.types.Integer(), 
                        "tracks":sqlalchemy.types.NVARCHAR(length=255)})    
    
#print(df_tracks.to_sql)
#print(df_artists.to_sql)
song_in_playlist=pd.read_sql_query('select count(*) from tracks_database;',conn)
query="""
        SELECT name, duration_ms
        FROM tracks_database
        where duration_ms=(SELECT MAX(duration_ms) FROM tracks_database)
        """
longest_song=pd.read_sql_query(query,con=engine)

query="""
        SELECT tracks, followers
        FROM artists_database
        ORDER BY followers DESC LIMIT 5;
        
      """
top_5_tracks_by_artist=pd.read_sql_query(query,con=engine)

query="""
        SELECT T.artist_name, T.popularity, A.a_popularity
        FROM tracks_database  T
        LEFT JOIN artists_database A
        ON T.artist_name=A.a_name
        Group By T.name
        
    """
left_join_tables=pd.read_sql_query(query,con=engine)

left_join_tables.corr(method='pearson')
correletion=left_join_tables['a_popularity'].corr(left_join_tables['popularity'])
print('Correlation between artist popularity and track popularity is: %f' % correletion)
sns.set(color_codes=True)
sns.regplot(pd.Series(left_join_tables["a_popularity"], name="Artist Popularity"), pd.Series(left_join_tables["popularity"],name="Track Popularity"), data=left_join_tables);
