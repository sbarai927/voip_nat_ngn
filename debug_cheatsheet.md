# Debug Cheat-Sheet — VoIP + NAT NGN Lab

## Asterisk / PJSIP CLI

| Goal                              | Command                            |
| --------------------------------- | ---------------------------------- |
| Launch live console (verbosity 5) | `sudo asterisk -rvvvvv`            |
| Change verbosity (0-5)            | `core set verbose 5`               |
| Toggle debug logs (0-5)           | `core set debug 5`                 |
| **Log every SIP frame**           | `pjsip set logger on`              |
| Log frames from one peer          | `pjsip set logger host <IP>`       |
| Show endpoint table               | `pjsip show endpoints`             |
| Show registration(s)              | `pjsip show registrations`         |
| List active channels              | `core show channels verbose`       |
| Codec translation matrix          | `core show translation`            |
| RTP stats per channel             | `rtp show stats <CALL-ID>`         |
| Reload configs                    | `dialplan reload`   `pjsip reload` |
| Inspect NAT flags per peer        | `pjsip show endpoint <id>`         |

Hint: Frame flood? Filter by Call-ID in Wireshark and pjsip set logger host.

## Cisco IOS

### General show / debug
```bash
show ip interface brief
show running-config | section <interface|router>
show ip route
debug ip packet detail        ! (⚠ very noisy)
```

### NAT / PAT
```bash
show ip nat translations
clear ip nat translation *    ! flush table
debug ip nat
```

### Serial & Clocking
```bash
show controllers serial 0/1/0
show interfaces serial 0/1/0
```

### SPAN / Mirror Verification
```bash
show monitor session 1
```

Tip: Lost packets? Check ACL counters: show access-lists.

## Wireshark Filters

| Task               | Display Filter                            |
| ------------------ | ----------------------------------------- |
| All SIP signalling | `sip`                                     |
| All RTP media      | `rtp`                                     |
| SIP **or** RTP     | `sip or rtp`                              |
| One call (Call-ID) | `sip.Call-ID contains <id>`               |
| Single peer        | `ip.addr == 10.3.0.3`                     |
| RTP dynamic ports  | `udp.port >= 10000 and udp.port <= 20000` |
| STUN keep-alive    | `stun`                                    |

### GUI Quick Wins

- Telephony ▶ VoIP Calls ▶ Flow Sequence — auto MSC.

- RTP ▶ Stream Analysis — jitter & loss per leg.

- Statistics ▶ I/O Graph — codec bitrate spikes.

## Troubleshooting Flow

- Confirm registration
```bash
pjsip show registrations
show ip nat translations | inc 5060
```
- Place test call and watch asterisk -rvvvvv
- No / one-way audio?
  - Wrong c= line in SDP → NAT

  - Check direct_media flags

  - Verify RTP PAT entries on R2 ```bash show ip nat translation | inc 10.3.2 ```

- Stuck at 200 OK / ACK
  - Contact header shows private IP → enable
   - ```bash
     rewrite_contact = yes
     rtp_symmetric  = yes
     force_rport    = yes
     ```
- Codec / transcoding errors
   - core show translation for paths

   - Limit endpoints to allow=alaw,ulaw

   - Look for “No translator path” warnings


## Repro Snippets

### Fire a test SIP invite (sipsak)

```bash
sipsak -s sip:3002@10.3.0.2 -u 3001 -a password -vv -r 1 -M \
       -B "Hello-World-Ping"
```

### Generate silent RTP (GStreamer)

```bash
gst-launch-1.0 audiotestsrc wave=silence ! alawenc ! rtppcmapay \
  ! udpsink host=10.3.2.3 port=50040
```
### Run NS-3 mini simulation
```bash
python scripts/network_simulation_ns3.py --scenario nat_stress --duration 60
```

## Cleanup Helpers

```bash
# Asterisk
pjsip send unregister all
database deltree registrar

# IOS
clear counters
configure replace flash:golden.cfg force

# Local
pkill -9 tshark   # stop captures
```
