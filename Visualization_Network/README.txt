%%%%%%%%%%%%%%%%%%%%%%  READ ME %%%%%%%%%%%%%%%%%%%%%%%

				Visualization of network

1) Currently:
    -"User-Topic Network.html" 
    Containing a percentage of Users as nodes. The Users were filtered based on their deegre range to make the visualization readable.
     - Node Radius: Mean Influence of User.
     - Node Color: Depending on the most proable topic of the user, based on the topic extraction methodology (15 different topics).
     - Links: Directed links without weights.
    
3) You need to serve the index.html as a server would.

Needs the output from Network_Gexf_Creator.jar. Moreover you have to specify an assesment_id e.g: http://localhost:8000/?assesment_id=example1/

Example Usage:

LINUX:

1) Go to folder containing index.html.
2) Set up a localserver. For example to do so, from terminal instance spawned in current folder run:
 > python -m SimpleHTTPServer 
3) The local host is accessible via all browsers (Chrome, Firefox etc) in the following URL: "localhost:8000/?assesment_id=example1/" (can also open "0.0.0.0:8000/?assesment_id=example1/")

WINDOWS:

1) Install from chrome store the app : Web Server for Chrome
2) Start the app from: chrome://apps/ 
3) Choose folder where index.html is located.
4) Tick box "Automatically show index.html"
5) That's it. Open up in browser the url presented (default: http://127.0.0.1:8887/?assesment_id=example1/) to see the network.

Questions/Errors:
bogas.ko@gmail.com




