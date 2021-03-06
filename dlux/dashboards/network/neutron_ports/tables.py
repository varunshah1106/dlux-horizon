# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Author: Dave Tucker <dave.j.tucker@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from horizon import tables


def get_port_link(datum):
    view = "horizon:network:neutron_ports:detail"
    if datum.id:
        #ToDo: Not sure why this works, but it does
        link = urlresolvers.reverse(view, args={datum.id})
    else:
        link = None
    return link


def get_network_link(datum):
    view = "horizon:network:neutron_networks:detail"
    if datum.id:
        #ToDo: Not sure why this works, but it does
        link = urlresolvers.reverse(view, args={datum.network_id})
    else:
        link = None
    return link


class NeutronPortsTable(tables.DataTable):
    id = tables.Column('id',
                       verbose_name=_('Identifier'),
                       link=get_port_link)
    name = tables.Column('name', verbose_name=_('Name'))
    network_id = tables.Column('network_id',
                               verbose_name=_("Network Identifier"),
                               link=get_network_link)
    tenant_id = tables.Column('tenant_id', verbose_name=_("Tenant Identifier"))

    class Meta:
        name = 'neutron_ports'
        verbose_name = _('Neutron Ports')
