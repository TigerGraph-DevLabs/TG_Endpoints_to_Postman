import cred
import pyTigerGraph as tg
import json

### Header
ma = {
    "name": cred.GRAPHNAME,
    "description": cred.GRAPHNAME,
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
}

gui_port = ["/api/ping", "/ts3/api/datapoints", "/informant/current-service-status", "/gsqlserver/gsql/schema", "/gsqlserver/gsql/queryinfo", "/gsqlserver/interpreted_query"]

### Create TG Connection
conn = tg.TigerGraphConnection(host=cred.URL, username=cred.USERNAME, password=cred.PASSWORD, graphname=cred.GRAPHNAME)
conn.apiToken = conn.getToken(conn.createSecret())

### Update based on version
ver = conn.getVer().split(".")
EXTRA_ENDPOINT = ""
if int(ver[0]) > 3 or (int(ver[0]) == 3 and int(ver[1]) > 6) or (int(ver[0]) == 3 and int(ver[1]) == 6 and int(ver[2]) > 0):
    EXTRA_ENDPOINT = "/restpp"

### Get Endpoints
enp = conn.getEndpoints(builtin = True, dynamic = True, static = True)

### Parse endpoints to items
item = []
var_to_description = {
    "{graph_name}": {
            "description": "(Optional) The name of the graph (REQUIRED in case of multiple graph in the database).",
            "key": "graph_name",
            "value": "{{graph_name}}"
    },
    "{requestid}": {
        "description": "(Optional) The id of a query request to be aborted, or \"all\" to abort all queries.",
        "key": "requestid",
        "value": "",
    },
    "{edge_type}": {
        "description": "(Optional) The type name of the edges. If omitted or specified as \"_\", then all edge types are permitted. If skipped, then target_vertex_type and target_vertex_id must be skipped too.",
        "key": "edge_type",
        "value": ""
    },
    "{vertex_type}": {
        "description": "(REQUIRED) The name of vertex type.",
        "key": "vertex_type",
        "value": ""
    },		
    "{vertex_id}": {
        "description": "(Optional) ID of a vertex of the given type (optional; if not provided all vertices of the given type are listed, subject to limits).",
        "key": "vertex_id",
        "value": ""
    },
    "{source_vertex_type}": {
        "description": "(REQUIRED) The type of the source vertex.",
        "key": "source_vertex_type",
        "value": ""
    },
    "{source_vertex_id}": {
        "description": "(REQUIRED) The primary_id of the source vertex.",
        "key": "source_vertex_id",
        "value": ""
    },
    "{target_vertex_type}": {
        "description": "(Optional) The type of the target vertex.",
        "key": "target_vertext_type",
        "value": ""
    },
    "{target_vertex_id}": {
        "description": "(Optional) The primary_id of the target vertex.",
        "key": "target_vertex_id",
        "value": ""
    }
}

link_var = [i[1:-1] for i in var_to_description]

for x in enp:
    query_arr = []

    for i in enp[x]["parameters"]:
        if i not in link_var:
            try: 
                val = enp[x]["parameters"]["default"]
            except:
                val = None
            query_arr.append({
                "key": i,
                "value": val,
                "description": "",
                "disabled": True
            })

    path_arr = []
    name_arr = []

    var_arr = []
    if x[-1] == "/":
        x = x[:-1]
    par = x.split("/")
    for i in par:
        if not (i[0] == "{" and i[-1] == "}"):
            name_arr.append(i)
            path_arr.append(i)
        else:
            path_arr.append("{" +i+ "}")
            try: 
                var_arr.append(var_to_description[i])
            except: 
                custom_var = {
                    "description": "",
                    "key": i[1:-1],
                    "value": ""
                }
                var_arr.append(custom_var)
    path_arr = path_arr[1:]

    auth = {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{token}}",
                    "type": "string"
                }
            ]
        }
    port = "{{port}}"

    for i in gui_port:
        if i in x:
            auth = {
                        "type": "basic",
                        "basic": [
                            {
                                "key": "password",
                                "value": "{{password}}",
                                "type": "string"
                            },
                            {
                                "key": "username",
                                "value": "{{username}}",
                                "type": "string"
                            },
                            {
                                "key": "showPassword",
                                "value": False,
                                "type": "boolean"
                            }
                        ]
                    }
            port = "{{port_gui}}"
    
    if "/requesttoken" in x:
        auth = {
					"type": "noauth"
				}

    it = {
        "name": "/".join(name_arr),
        "request": {
            "auth": auth,
            "method": name_arr[0].split(" ")[0],
            "header": [],
            "url": {
                "raw": "{{protocol}}://{{url}}:" + port + EXTRA_ENDPOINT + "/" + "/".join(path_arr),
                "protocol": "{{protocol}}",
                "host": [
                    "{{url}}"
                ],
                "port": port,
                "path": path_arr
            },
            "description": "https://docs.tigergraph.com/tigergraph-server/current/api/built-in-endpoints"
        },
        "response": []
    }
    
    if len(var_arr) > 0:
        it["request"]["url"]["variable"] = var_arr
    if len(query_arr) > 0:
        it["request"]["url"]["query"] = query_arr

    item.append(it)

### Create a JSON file
json_object = json.dumps({"info": ma, "item": item}, indent=4)

with open(cred.OUTPUT_FILE, "w") as outfile:
    outfile.write(json_object)
