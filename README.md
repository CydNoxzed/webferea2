# Webferea2

This is a web single-user counterpart to the GTK+ news aggregator [Liferea](https://lzone.de/liferea/ "Liferea"). Webferea syncs the sqlite-database of Liferea over http on a server which runs your Webferea instance. You can read selected feeds over the webinterface and flag their items as *read* or *marked*. On the next sync, the flags are applied to your local sqlite-database of Liferea and the merged database will be uploaded to the server again.

You can only access your feed list on the web with a correct password, which you can set in the config. In the config you can list all feeds which unread items should be listed in Webferea.

The layout of the webinterface is optimized for the use on a smartphone.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes or on your server for production usage.

### Prerequisites

- [python >=3.8](https://www.python.org)
- [Flask >=1.1.2](http://flask.pocoo.org)

### Installing

Clone the files from the repository into a directory on your server and a directory on your desktop pc, who runs Liferea.

```
git clone https://github.com/CydNoxzed/webferea2.git
```

Run ```pip install -r requirements.txt``` to install all dependencies.


### Server

Copy the example-config.json to instance/config.json and edit it, till it fit your needs.

You can start webferea by creating a screen/tmux-session and start the *run.sh* in it. You should proxy the traffic over a webserver to use SSL.
Please change the ENV variables and the [SECRET_KEY](https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY) in the run.sh

If you want to use FCGI, you need to customize Webferea. You can use the [flask fastcgi tutorial](https://flask.palletsprojects.com/en/1.1.x/deploying/fastcgi/).

#### Configuration

The configuration should be placed as "config.json" inside the instance folder.

- USERNAME: Name for the login on the webfrontend
- PASSWORD: Password for the login on the webfrontend
- NODES: Names of the feeds who should be shown in webferea (that is the title of the subscription you can edit in liferea). Should be a valid json list.
- DATABASE: Name of the database on the server (default "liferea.db")
- ITEMS_PER_PAGE: number of items on a page (default: 10)
- WORDS_PER_MINUTE: Words you can read per minute. Used to calculate the aprox. reading time (default: 240)
- SHOW_READ_ENTITIES_PER_DEFAULT: Should the already read items be seen? (Default: False)


#### lighttpd
```
$HTTP["host"]=~"myserver.de" {
    proxy.server = ( "" => ((
        "host" => "127.0.0.1",
        "port" => "8000",
    )))
}
```

#### nginx
```
server {
    server_name myserver.de;
    proxy_set_header X-Forwarded-For $remote_addr;
    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_pass http://127.0.0.1:8000;
        proxy_buffering off;
        proxy_connect_timeout  36000s;
        proxy_read_timeout  36000s;
        proxy_send_timeout  36000s;
        send_timeout  36000s;
        client_max_body_size 0;
    }
}
```

### Client

The clientscript ```webferea_sync.py``` will upload/download the liferea.db from you desktop client to the server instance and merge its read/mark contents into your local liferea.db.

See ```webferea_sync.py -h``` for usage.

Example: ```webferea_sync.py myserver.de username password```

After the sync you can restart Liferea on your local machine, to see the proper sums of the unread items on every feed.

## Versioning

This project uses [SemVer](http://semver.org/) for versioning.
For the changelog, see the [CHANGELOG.md](CHANGELOG.md) file for details.

## License

This project is licensed under the GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details


