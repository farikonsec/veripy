from contrib.rfc3315.constants import *
from contrib.rfc3633.dhcpv6_pd import DHCPv6PDHelper
from scapy.all import *
from veripy.assertions import *


class RenewMessageTestCase(DHCPv6PDHelper):
    """
    Requesting Router Initiated: Renew Message

    Verify that a device can properly interoperate while using DHCPv6-PD

    @private
    Source:         IPv6 Ready DHCPv6 Interoperability Test Suite (Section 4.2)
    """

    def run(self):
        prefix, p = self.do_dhcpv6_pd_handshake_as_client(self.target(1), self.node(1))

        self.logger.info("Acquired the prefix %s from the DR (T1=%d)." % (prefix, p[DHCP6OptIA_PD].T1))

        for i in range(0, 2):
            self.ui.wait(p[DHCP6OptIA_PD].T1)

            self.node(1).clear_received()
            self.logger.info("Sending a DHCPv6 Renew message...")
            self.node(1).send(
                IPv6(src=str(self.node(1).link_local_ip()), dst=str(AllDHCPv6RelayAgentsAndServers))/
                    UDP(sport=DHCPv6SourcePort, dport=DHCPv6DestPort)/
                        self.build_dhcpv6_pd_renew(p, self.target(1), self.node(1)))

            self.logger.info("Checking for a DHCPv6 Reply message...")
            r1 = self.node(1).received(src=self.target(1).link_local_ip(), type=DHCP6_Reply)
            assertEqual(1, len(r1), "expected to receive a DHCPv6 Reply message")

            assertHasLayer(DHCP6OptIA_PD, r1[0], "expected the DHCPv6 Reply to contain an IA for Prefix Delegation")
            assertHasLayer(DHCP6OptIAPrefix, r1[0], "expected the DHCPv6 Reply to contain an IA Prefix")
            