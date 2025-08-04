# VoIP-NAT-NGN Lab

> **Reproducible reference implementation of a small VoIP service-provider  
> network (Asterisk 18 + Cisco IOS) with NAT traversal, peer-to-peer & proxy
> modes, traffic monitoring, and inter-provider SIP trunking.**

&nbsp;

| Milestone | Focus | Status |
|-----------|-------|--------|
| **MS-1** | Basic VoIP service provider (LAN-A / LAN-C) | ✅ complete |
| **MS-2** | Monitoring & traffic analysis (SPAN, Wireshark) | ✅ complete |
| **MS-3** | Remote site with NAT, peer-to-peer RTP | ✅ complete |
| **MS-4** | Inter-provider SIP trunk, transcoding | ✅ complete |

---

<details open>
<summary><strong>Table of Contents</strong></summary>

1. [Objective](#objective)  
2. [Quick Start](#quick-start)  
3. [Repository Layout](#repository-layout)  
4. [Milestones at a Glance](#milestones-at-a-glance)  
5. [How to Debug](#how-to-debug)  
6. [Re-Playing Captures](#re-playing-captures)  
7. [NS-3 Simulation](#ns-3-simulation)  
8. [Known Issues / TODO](#known-issues--todo)
9. [Advanced Debugging Cookbook](#advanced-debugging-cookbook)
10. [One-Click Sandbox (Vagrant + Docker)](#one-click-sandbox)
11. [Credits](#credits)
12. [Contact](#contact)
</details>

## Objective

This lab was carried out as a ULP completion requirement for the course **Next Generation Networks** (SS 2024) taught by **Prof. Dr. Andreas Grebe** at **Technische Hochschule Köln**.

## Quick Start
```bash
git clone https://github.com/YOUR-USER/voip_nat_ngn.git
cd voip_nat_ngn

# --- Asterisk VM -------------------------------------------------
sudo apt update && sudo apt install asterisk
sudo cp configs/asterisk/*.conf /etc/asterisk/
sudo systemctl restart asterisk

# --- Cisco IOS (GNS3 or real gear) -------------------------------
#   → Import the startup-configs below or paste via console.

verify:

asterisk -rx "pjsip show endpoints"           # 3001 / 3002 => OK
show ip nat translations | count              # on R2
```
Dial 3001 ↔ 3002 (proxy) or 2XXX to reach Team-2 via SIP trunk.

## Repository Layout  

The directory structure of this project is as follows:
```bash
.
├── configs/
│ ├── asterisk/
│ │ ├── extensions_final.conf
│ │ ├── modules.conf
│ │ ├── pjsip_final.conf
│ │ └── pjsip.conf
│ └── network/
│ ├── router_R1_border.txt
│ ├── router_R2_remote_NAT.txt
│ └── switch_S1_S2_common_campus.txt
│
├── diagrams/ # 📊 Sequence charts & logical topologies
│ ├── sip_registration.png
│ └── voip_agents_call_establishment_via_server.png
│
├── docs/ # 📑 Generated or hand-written design docs
│ └── report.pdf
│
├── images/ # 📸 Extra screenshots referenced in README / report
│ ├── 200 ok peer.png
│ ├── 200 ok proxy.png
│ ├── auth.png
│ ├── bothserverreg.png
│ ├── conference.png
│ ├── conversion.png
│ ├── debug.png
│ ├── extencodes…
│ └── … (many more)
│
├── milestones/ # 🎯 Original PDF task sheets (MS1-MS6)
│ ├── NGN_Default_Lab_MS1.pdf
│ ├── NGN_Default_Lab_MS2.pdf
│ ├── NGN_Default_Lab_MS3.pdf
│ └── NGN_Default_Lab_MS4-MS6.pdf
│
├── scripts/ # 🐍 Helper tooling & simulation
│ └── network_simulation_ns3.py
│
├── wireshark_captures/ # 🕵️ .pcapng traces per milestone
│ ├── extras/
│ │ ├── Conference_setup.pcapng
│ │ └── DTMF.pcapng
│ ├── ms_2/
│ │ ├── proxy_mode.pcapng
│ │ └── registration.pcapng
│ ├── ms_3/
│ │ ├── calling_LAN\ A\ to\ C.pcapng
│ │ ├── calling_LAN\ C\ to\ A.pcapng
│ │ ├── ms3lanAtoCS.pcapng
│ │ ├── ms3lanCtoAS.pcapng
│ │ ├── ms3voipM.pcapng
│ │ └── ms3voipS.pcapng
│ └── ms_4/
│ ├── binding_trancoding_all\ teams.pcapng
│ ├── calling_team2to3.pcapng
│ ├── calling_team3to2.pcapng
│ ├── ms4conference.pcapng
│ ├── ms4translation.pcapng
│ ├── reg_both_servers_team\ 2\ and\ 3.pcapng
│ └── transcoding\ team1\ and\ 3.pcapng
│── debug_cheatsheet.md
└── README.md # 👉 You are here

```


## Milestones at a Glance

| MS    | Scope                              | Key Config(s)                         | Main Capture                           |
| ----- | ---------------------------------- | ------------------------------------- | -------------------------------------- |
| **1** | Basic SP VoIP (LAN-A ↔ LAN-C)      | `pjsip.conf`, `extensions_final.conf` | `registration.pcapng`                  |
| **2** | Monitoring / SPAN                  | `switch_S1_S2_common_campus.txt`      | `proxy_mode.pcapng`                    |
| **3** | NAT & P2P RTP                      | `router_R2_remote_NAT.txt`            | `calling_LAN C to A.pcapng`            |
| **4** | Inter-provider trunk + transcoding | `pjsip_final.conf`                    | `reg_both_servers_team 2 and 3.pcapng` |

## How to Debug

### Asterisk
pjsip set logger on
core set verbose 5

### IOS
show ip nat translations
clear ip nat translation *

### Wireshark
Display filter  -  sip || rtp           # all VoIP
                 -  rtp && udp.port==50040
                 
Additional tips live in debug_cheatsheet.md

## Re-Playing Captures

wireshark wireshark_captures/ms_3/calling_LAN\ C\ to\ A.pcapng
- Wireshark → Telephony → RTP → Stream Analysis → Save payload

## NS-3 Simulation

```bash
cd scripts
# ns-3.39 + Python bindings required
./waf configure --enable-python-binding
./waf --run scratch/network_simulation_ns3
```
## Known Issues / TODO

- Transcoding warning (lost frame(s)): benign in the lab.

- 30 s call drop → tune contact_expiration_check_interval (Asterisk) or router NAT timeout.

- GNS3 IOSv may need no ip cef for accurate NAT stats.

## Advanced Debugging Cookbook

<details>
<summary>Open cheat-sheet</summary>

### SIP Torture Tests
| Goal | Command |
|------|---------|
| Flood UA with malformed INVITEs | `sipp -sf uac_invite_fuzz.xml 10.3.0.2 -r 50 -m 1000` |
| Check authentication replay-attack handling | `sipp -sf auth_replay.xml -auth_md5 3001:password 10.3.0.2` |

*Logs to watch*  
```bash
asterisk -rx "logger rotate"
tail -F /var/log/asterisk/full | grep -Ei 'AUTH|RESPOND'
```

### RTP Clock-Drift & Jitter
```bash
# Capture 5 s audio from active stream
rtpdump -F dump rtp@10.3.0.3/50040 > trace.rtp
rtpplay trace.rtp | \
   tshark -V - | grep -E 'Timestamp|Sequence'
```
ΔTimestamp / ΔSeq should remain ~20 ms / 1; large spikes ⇒ clock mismatch.

### IOS Packet-Level Tracing
```bash
conf t
interface g0/0/1
 ip packet-tracer input udp 10.3.2.3 50040 10.3.0.3 50040 detail
end
```
Shows the entire CEF path, NAT look-ups, ACL hits and drops.
</details>

## One-Click Sandbox (Vagrant + Docker)

<details>

```bash
### 1. Bring up two “routers” (VyOS) + one Asterisk container
cd reproducible_lab/
vagrant up         # pulls boxes & boots

### 2. SSH into Asterisk VM, copy configs
vagrant ssh asterisk
sudo cp /vagrant/configs/asterisk/*.conf /etc/asterisk/
sudo systemctl restart asterisk

### 3. Inject Cisco configs into VyOS (native syntax already converted)
vagrant ssh router_r1  # or router_r2
configure
load /vagrant/configs/network/router_R1_border.vyos
commit && save
```
</details>


## Credits

- Course sheets and instructor © Prof. Dr. A. Grebe, TH Köln – see milestones/.
- Config snippets adapted from Mastering Asterisk (Packt 2020).

## Contact

For any questions or issues, please contact:
 - Suvendu Barai
 - Email: suvendu.barai@smail.th-koeln.de
