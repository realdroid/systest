from flask import flash, Flask, Markup, redirect, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from os.path import abspath, dirname, join
import urllib2,requests, json

app = Flask(__name__)

_cwd = dirname(abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + join(_cwd, 'cluster.db')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Ihatehairlp720@localhost/cluster'
app.debug=True
db = SQLAlchemy(app)


class ClusterDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(), unique=True)
    num_nodes = db.Column(db.Integer)
    name = db.Column(db.String())
    internal_subnet = db.Column(db.String())
    external_subnet = db.Column(db.String())
    version = db.Column(db.String())
    read_io_ppm = db.Column(db.Integer)
    num_iops = db.Column(db.Integer)
    content_cache_hit_ppm = db.Column(db.Integer)
    num_write_iops = db.Column(db.Integer)

    def __init__(self, ip_address, num_nodes, name, internal_subnet, external_subnet, version, read_io_ppm, num_iops, content_cache_hit_ppm, num_write_iops):
        self.ip_address = ip_address
        self.name = name
        self.internal_subnet = internal_subnet
        self.num_nodes = num_nodes
        self.external_subnet = external_subnet
        self.version = version
        self.read_io_ppm = read_io_ppm
        self.num_iops = num_iops
        self.content_cache_hit_ppm = content_cache_hit_ppm
        self.num_write_iops = num_write_iops

    def __repr__(self):
        return '<ClusterDetails %r>' %self.ip_address


class TableEnteries(object):
    def __init__(self, ip_address, name, subnet):
        self.ip_address = ip_address
        self.name = name
        self.subnet = subnet

@app.route('/')
@app.route('/home')
def index():
    return render_template('/home.html')


@app.route('/enter_details', methods=['POST'])
def enter_details():
    ip_address = request.form['ip_address']
    username = request.form['username']
    password = request.form['password']
    perform_query(ip_address, username, password)
    return render_template('/home.html')


def perform_query(ip_address, username, password):
    ip_address=ip_address+":9440"
    rest_call = "https://%s/PrismGateway/services/rest/v1/clusters/" % ip_address
    response = requests.get(rest_call,
                            auth=(username, password),
                            verify=False)
    data = response.json()
    for i in data['entities']:
        internal_subnet = i['internalSubnet']
        external_subnet = i['externalSubnet']
        name = i['name']
        num_nodes = i['numNodes']
        version = i['version']
        for j in i['stats']:
            if j == 'read_io_ppm':
                read_io_ppm = i['stats'][j]
            elif j == 'num_iops':
                num_iops = i['stats'][j]
            elif j == 'content_cache_hit_ppm':
                content_cache_hit_ppm = i['stats'][j]
            elif j == 'num_write_iops':
                num_write_iops = i['stats'][j]

    insert = ClusterDetails(ip_address, num_nodes, name, internal_subnet, external_subnet, version, read_io_ppm, num_iops, content_cache_hit_ppm, num_write_iops)
    db.session.add(insert)
    db.session.commit()
    return


@app.route('/delete')
def delete():
    ClusterDetails.query.delete()
    db.session.commit()
    return render_template('/home.html')


@app.route('/view_details')
def view_details():
    MyCluster = ClusterDetails.query.all()
    OneCluster = ClusterDetails.query.filter_by(ip_address="10.1.1.1").all()
    return render_template('/view_details.html', MyCluster=MyCluster, OneCluster=OneCluster)

if __name__ == "__main__":
    app.run()