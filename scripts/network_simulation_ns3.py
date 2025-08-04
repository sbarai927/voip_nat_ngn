import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.point_to_point

# Create a network simulation object
sim = ns.core.NodeContainer()
sim.Create(2)  # Create two nodes

# Create a point-to-point link between the nodes
pointToPoint = ns.point_to_point.PointToPointHelper()
pointToPoint.SetDeviceAttribute("DataRate", ns.core.StringValue("5Mbps"))
pointToPoint.SetChannelAttribute("Delay", ns.core.StringValue("2ms"))

devices = pointToPoint.Install(sim)

# Install protocol stack
stack = ns.internet.InternetStackHelper()
stack.Install(sim)

# Assign IP addresses to the nodes
address = ns.internet.Ipv4AddressHelper()
address.SetBase(ns.network.Ipv4Address("10.1.1.0"), ns.network.Ipv4Mask("255.255.255.0"))
interfaces = address.Assign(devices)

# Add routing
ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

# Create a traffic source and sink
source = ns.applications.OnOffHelper("ns3::UdpSocketFactory", ns.network.Address(ns.network.InetSocketAddress(interfaces.GetAddress(1), 9)))
source.SetAttribute("OnTime", ns.core.StringValue("ns3::ConstantRandomVariable[Constant=1]"))
source.SetAttribute("OffTime", ns.core.StringValue("ns3::ConstantRandomVariable[Constant=0]"))

sourceApps = source.Install(sim.Get(0))
sourceApps.Start(ns.core.Seconds(1.0))
sourceApps.Stop(ns.core.Seconds(10.0))

sink = ns.applications.UdpEchoServerHelper(9)
sinkApps = sink.Install(sim.Get(1))
sinkApps.Start(ns.core.Seconds(0.0))
sinkApps.Stop(ns.core.Seconds(10.0))

# Run simulation
ns.core.Simulator.Stop(ns.core.Seconds(10.0))
ns.core.Simulator.Run()
ns.core.Simulator.Destroy()
