# Topología de Red - Tótem Municipal

## Diagrama de Red

```
                    Internet / VPN IPSEC
                           |
                    [Router UniFi]
                           | Gig0/0
                           |
                    [Cloud Cld]
                           | Gig9
                           | Eth0/0
                    [Firewall 5505]
                           | Eth0/1
                           |
              [Switch 2960-24TT]
                    /          \
               Fa0/1          Fa0/2
                 /              \
        [DMZ Network]      [Server-PT SRV-BD]
             |
        [Server-PT SRV-WEB-API]
```

## Direccionamiento IP

| Dispositivo | Interfaz | IP | Máscara | Gateway |
|------------|----------|-----|---------|---------|
| Router UniFi | Gig0/0 | 192.168.1.1 | 255.255.255.0 | - |
| Router UniFi | Gig0/2 | 10.0.0.1 | 255.255.255.0 | - |
| Cloud Cld | Gig9 | 10.0.0.2 | 255.255.255.0 | 10.0.0.1 |
| Cloud Cld | Gig8 | 172.16.0.1 | 255.255.255.0 | - |
| Firewall 5505 | Eth0/0 | 172.16.0.2 | 255.255.255.0 | 172.16.0.1 |
| Firewall 5505 | Eth0/1 | 192.168.2.1 | 255.255.255.0 | - |
| Switch 2960-24TT | Fa0/24 | 192.168.2.2 | 255.255.255.0 | 192.168.2.1 |
| Switch2 | Fa0/1 | 192.168.3.1 | 255.255.255.0 | - |
| TOTEM-01 | Fa0 | 192.168.3.10 | 255.255.255.0 | 192.168.3.1 |
| PC-FUNCIONARIO | Fa0 | 192.168.3.11 | 255.255.255.0 | 192.168.3.1 |
| SRV-WEB-API | Fa0 | 192.168.4.10 | 255.255.255.0 | 192.168.4.1 |
| SRV-BD | Fa0 | 192.168.4.11 | 255.255.255.0 | 192.168.4.1 |

## Requerimientos Técnicos

### Hardware
| Dispositivo | Cantidad | Función |
|------------|----------|---------|
| Router UniFi | 1 | Acceso a internet y VPN |
| Switch Cisco 2960-24TT | 2 | Conmutación de red |
| Firewall Cisco ASA 5505 | 1 | Seguridad de perímetro |
| Cloud Cld | 1 | Cloud computing |
| PC Tótem | 1 | Interfaz ciudadana |
| PC Funcionario | 1 | Administración |
| Servidor Web/API | 1 | Backend |
| Servidor BD | 1 | Base de datos |

### Software
| Software | Versión | Función |
|----------|---------|---------|
| Kivy | 2.3.1 | Interfaz del tótem |
| FastAPI | 0.100+ | API REST |
| SQLite | 3.x | Base de datos local |
| Python | 3.12 | Lenguaje de programación |
| AWS | - | Infraestructura cloud |
| VPN IPSec | - | Conexión segura |

### EPP (Equipo de Protección Personal)
- Guantes de protección
- Gafas de seguridad
- Servicio de electricista certificado

## Configuraciones Realizadas

1. **Configuración de VPN IPSec** entre Router UniFi y Cloud Cld
2. **Configuración de Firewall 5505** con reglas de acceso
3. **Configuración de VLANs** en Switch 2960-24TT
4. **Configuración de Port Forwarding** para servicios web
