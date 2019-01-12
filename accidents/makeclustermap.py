import folium
from folium.plugins import MarkerCluster

class MarkerClusterScript(MarkerCluster):
    def __init__(self, data, callback, popup=None):
        from jinja2 import Template
        super(MarkerClusterScript, self).__init__([])
        self._name = 'Script'
        self._data = data
        self._popup = popup
        if callable(callback):
            from flexx.pyscript import py2js
            self._callback = py2js(callback, new_name="callback")
        else:
            self._callback = "var callback = {};".format(_callback)

        self._template = Template(u"""
            {% macro script(this, kwargs) %}
            (function(){
                var data = {{this._data}};
                var map = {{this._parent.get_name()}};
                var cluster = L.markerClusterGroup();
                {{this._callback}}

                for (var i = 0; i < data.length; i++) {
                    var row = data[i];
                    var marker = callback(row, popup='names');
                    marker.addTo(cluster);
                }

                cluster.addTo(map);
            })();
            {% endmacro %}
                        """)
        
def create_marker(row, popup=None):
    """Returns a L.marker object"""
    icon = L.AwesomeMarkers.icon({markerColor: row.color})    
    marker = L.marker(L.LatLng(row.latitude, row.longitude))
    marker.setIcon(icon)
    marker.bindPopup(row.causa_acidente+' '+row.velocidade_via +' '+row.data_inversa + ' ' + row.latitude + ' ' + row.longitude)
    return marker
