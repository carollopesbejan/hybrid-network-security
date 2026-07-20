# 🛡️ Sistema Híbrido de Detecção e Contenção de Ameaças em Rede

Autômato Celular com Consenso Distribuído e Agentes de Defesa para Segurança de Redes

## 📖 Sobre o Projeto

Este projeto implementa um sistema híbrido de segurança de redes usando autômatos celulares. O modelo combina:

- 🔍 **Detecção por sensores** com sistema de votação distribuída
- 🛡️ **Firewalls móveis** que perseguem e contêm ameaças
- 💉 **Aplicação de patches** para imunizar nós comprometidos
- 🗳️ **Consenso entre vizinhos** para reduzir falsos positivos

### Estados das Células

| Estado | Cor | Significado |
|--------|-----|-------------|
| 0 | 🟢 Verde | Normal (saudável, vulnerável) |
| 1 | 🔴 Vermelho | Infectado (propagando malware) |
| 2 | 🟡 Amarelo | Sob Suspeita (sensor detectou anomalia) |
| 3 | ⚫ Cinza | Em Quarentena (isolado por firewall) |
| 4 | 🔵 Azul | Vacinado (patch aplicado, imune) |

## 🚀 Instalação

```bash
pip install -r requirements.txt