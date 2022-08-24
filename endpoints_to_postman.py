import cred
import pyTigerGraph as tg
import json

### Header
ma = {
    "name": cred.OUTPUT_FILE,
    "description": cred.GRAPHNAME,
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
}

gui_port = ["/api/ping", "/ts3/api/datapoints", "/informant/current-service-status", "/gsqlserver/gsql/schema", "/gsqlserver/gsql/queryinfo", "/gsqlserver/interpreted_query"]

### Create TG Connection
if cred.URL[:8] != "https://":
    cred.URL = "https://" + cred.URL
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

    if not port == "{{port_gui}}":
        path_arr = ['restpp'] + path_arr

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

    if {'key': 'query', 'value': None, 'description': '', 'disabled': True} in query_arr: # Remove extra query parameter
        query_arr.remove({'key': 'query', 'value': None, 'description': '', 'disabled': True})
    
    if len(var_arr) > 0:
        it["request"]["url"]["variable"] = var_arr
    if len(query_arr) > 0:
        it["request"]["url"]["query"] = query_arr

    item.append(it)

### Add Hard-Coded Endpoints
hard_coded_endpoints = [
		{
			"name": "GET /gsqlserver/gsql/schema",
			"protocolProfileBehavior": {
				"disableBodyPruning": True,
				"followOriginalHttpMethod": True
			},
			"request": {
				"auth": {
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
				},
				"method": "GET",
				"header": [],
				"body": {
					"mode": "file",
					"file": {}
				},
				"url": {
					"raw": "{{protocol}}://{{url}}:{{port_gui}}/gsqlserver/gsql/schema?graph={{graph_name}}",
					"protocol": "{{protocol}}",
					"host": [
						"{{url}}"
					],
					"port": "{{port_gui}}",
					"path": [
						"gsqlserver",
						"gsql",
						"schema"
					],
					"query": [
						{
							"key": "graph",
							"value": "{{graph_name}}",
							"description": "(REQUIRED) Name of graph."
						},
						{
							"key": "type",
							"value": "",
							"description": "(Optional) The name of either a vertex type or an edge type.",
							"disabled": True
						}
					]
				},
				"description": "If a vertex or edge name is provided for the `type` parameter: returns the definition of the requested vertex or edge type.\n\nIf no `type` parameter is specified: returns the schema of a graph. The output contains three top-level elements: `GraphName`, `VertexTypes` and `EdgeTypes`.\n\nhttps://docs.tigergraph.com/dev/restpp-api/built-in-endpoints#get-the-graph-schema-get-gsql-schema"
			},
			"response": []
		},
		{
			"name": "GET /gsqlserver/gsql/udtlist",
			"protocolProfileBehavior": {
				"disableBodyPruning": True,
				"followOriginalHttpMethod": True
			},
			"request": {
				"auth": {
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
				},
				"method": "GET",
				"header": [],
				"body": {
					"mode": "file",
					"file": {}
				},
				"url": {
					"raw": "{{protocol}}://{{url}}:{{port_gui}}/gsqlserver/gsql/udtlist",
					"protocol": "{{protocol}}",
					"host": [
						"{{url}}"
					],
					"port": "{{port_gui}}",
					"path": [
						"gsqlserver",
						"gsql",
						"udtlist"
					]
				},
				"description": "Returns the definition of User Defined Types (UDTs)."
			},
			"response": []
		},
		{
			"name": "POST /gsqlserver/interpreted_query",
			"request": {
				"auth": {
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
				},
				"method": "POST",
				"header": [],
				"body": {
					"mode": "raw",
					"raw": "INTERPRET QUERY (<params>) FOR GRAPH <graph_name> {\n    <statements>;\n}",
					"options": {
						"raw": {
							"language": "text"
						}
					}
				},
				"url": {
					"raw": "{{protocol}}://{{url}}:{{port_gui}}/gsqlserver/interpreted_query",
					"protocol": "{{protocol}}",
					"host": [
						"{{url}}"
					],
					"port": "{{port_gui}}",
					"path": [
						"gsqlserver",
						"interpreted_query"
					]
				},
				"description": "This endpoint runs a GSQL query in Interpreted Mode. The query body should be supplied at the data payload, and the query's parameters are supplied as the URL's query string.\n\nhttps://docs.tigergraph.com/dev/restpp-api/built-in-endpoints#post-gsqlserver-interpreted_query-run-an-interpreted-query"
			},
			"response": []
		},
		{
			"name": "GET /requesttoken",
			"request": {
				"auth": {
					"type": "noauth"
				},
				"method": "GET",
				"header": [],
				"url": {
					"raw": "{{protocol}}://{{url}}:{{port}}/restpp/requesttoken?secret={{secret}}",
					"protocol": "{{protocol}}",
					"host": [
						"{{url}}"
					],
					"port": "{{port}}",
					"path": [
                        "restpp",
						"requesttoken"
					],
					"query": [
						{
							"key": "secret",
							"value": "{{secret}}",
							"description": "(REQUIRED) The user's secret."
						},
						{
							"key": "lifetime",
							"value": "",
							"description": "(Optional) The lifetime for the token, in seconds. The default is one month, approximately 2.6 million seconds.",
							"disabled": True
						}
					]
				},
				"description": "Returns a token (that is required for authorisation of other REST++ requests) based on a secret (created in the database by `CREATE SECRET`).\n\nThis endpoint is available and works only if [REST++ authentication](https://docs.tigergraph.com/admin/admin-guide/user-access-management/user-privileges-and-authentication#rest-authentication)  is enabled.\n\nhttps://docs.tigergraph.com/dev/restpp-api/restpp-requests#requesting-a-token-with-get-requesttoken"
			},
			"response": []
		},
		{
			"name": "PUT /requesttoken",
			"request": {
				"auth": {
					"type": "noauth"
				},
				"method": "PUT",
				"header": [],
				"url": {
					"raw": "{{protocol}}://{{url}}:{{port}}/restpp/requesttoken?secret={{secret}}&token={{token}}",
					"protocol": "{{protocol}}",
					"host": [
						"{{url}}"
					],
					"port": "{{port}}",
					"path": [
                        "restpp",
						"requesttoken"
					],
					"query": [
						{
							"key": "secret",
							"value": "{{secret}}",
							"description": "(REQUIRED) The user's secret."
						},
						{
							"key": "token",
							"value": "{{token}}",
							"description": "(REQUIRED) The token to be refreshed."
						},
						{
							"key": "lifetime",
							"value": "",
							"description": "(Optional) The lifetime for the token, in seconds. The default is one month, approximately 2.6 million seconds.",
							"disabled": True
						}
					]
				},
				"description": "Refreshes a token (that is required for authorisation of other REST++ requests) based on a secret (requested via `GET_requesttoken`).\n\nThis endpoint is available and works only if [REST++ authentication](https://docs.tigergraph.com/admin/admin-guide/user-access-management/user-privileges-and-authentication#rest-authentication)  is enabled.\n\nhttps://docs.tigergraph.com/dev/restpp-api/restpp-requests#refreshing-tokens"
			},
			"response": []
		},
		{
			"name": "DELETE /requesttoken",
			"request": {
				"auth": {
					"type": "noauth"
				},
				"method": "DELETE",
				"header": [],
				"url": {
					"raw": "{{protocol}}://{{url}}:{{port}}/restpp/requesttoken?secret={{secret}}&token={{token}}",
					"protocol": "{{protocol}}",
					"host": [
						"{{url}}"
					],
					"port": "{{port}}",
					"path": [
                        "restpp",
						"requesttoken"
					],
					"query": [
						{
							"key": "secret",
							"value": "{{secret}}",
							"description": "(REQUIRED) The user's secret."
						},
						{
							"key": "token",
							"value": "{{token}}",
							"description": "(REQUIRED) The token to be deleted."
						}
					]
				},
				"description": "Deletes a token (that is required for authorisation of other REST++ requests).\n\nThis endpoint is available and works only if [REST++ authentication](https://docs.tigergraph.com/admin/admin-guide/user-access-management/user-privileges-and-authentication#rest-authentication)  is enabled.\n\nhttps://docs.tigergraph.com/dev/restpp-api/restpp-requests#deleting-tokens"
			},
			"response": []
		}
	]

### Create a JSON file
json_object = json.dumps({"info": ma, "item": item + hard_coded_endpoints}, indent=4)

with open(f"{cred.OUTPUT_FILE}.postman_collection.json", "w") as outfile:
    outfile.write(json_object)


### Create an environment
url = cred.URL.split("//")[-1]
if url[-1] == "/": url = url[:-1]
env = {
	"name": cred.ENVIRONMENT_FILE,
	"values": [
		{
			"key": "url",
			"value": url,
			"enabled": True
		},
		{
			"key": "graph_name",
			"value": cred.GRAPHNAME,
			"enabled": True
		},
		{
			"key": "token",
			"value": conn.apiToken,
			"enabled": True
		},
		{
			"key": "secret",
			"value": conn.createSecret(),
			"enabled": True
		},
		{
			"key": "username",
			"value": cred.USERNAME,
			"enabled": True
		},
		{
			"key": "password",
			"value": cred.PASSWORD,
			"enabled": True
		},
		{
			"key": "port",
			"value": "443",
			"enabled": True
		},
		{
			"key": "protocol",
			"value": "https",
			"enabled": True
		}
	],
	"_postman_variable_scope": "environment"
}

### Write the environment file
with open(f"{cred.ENVIRONMENT_FILE}.postman_environment.json", "w") as outfile:
    outfile.write(json.dumps(env, indent=4))