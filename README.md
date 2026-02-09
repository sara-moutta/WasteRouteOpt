# WasteRouteOpt: Sector-Based Vehicle Routing Optimization for Municipal Solid Waste Collection

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://img.shields.io/badge/DOI-pending-orange.svg)](https://github.com/smmoutta-uesc/WasteRouteOpt)

This repository contains the complete implementation of the routing optimization framework proposed in our study:

> **Moutta, Sara Meira, et al. (2026).**  
> *"Sector-based vehicle routing optimization for scalable municipal solid waste collection."*  
> IEEE Access [Under Review]

---

## 🎯 Methodological Overview

This framework implements a sector-based Vehicle Routing Problem (VRP) optimization approach for municipal solid waste collection systems.

Large urban service regions are decomposed into operational sectors, and a guided local search metaheuristic is applied independently to each sector, reducing computational cost while preserving solution quality.

---

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/smmoutta-uesc/WasteRouteOpt.git
cd WasteRouteOpt
```

2. **Insttall dependences**
```
pip install -r requirements.txt
```

### Running the simulation

The simulation is implemented as command line interface.
```bash
python run.py
```
## 📊 Features

- ```bash
python -m src.main
```
## 📊 Features

- Sector-based VRP optimization
- Capacity-constrained routing
- Guided Local Search metaheuristic
- Automatic multi-region execution
- Route visualization (PNG)
- Formatted route logs (TXT)
- Total distance performance metrics

Results are generated locally and stored in:
```
results/
 └── execution_date/
     ├── *_rotas.txt
     ├── *_grafico.png
     └── distancia_total_geral.txt
```

## 📁 Repository Structure
```
WasteRouteOpt/
├── README.md
├── LICENSE
├── run.py
├── src/
│   └── routing_optimizer.py
├── data/
│   ├── 275_points/
│   └── 2093_points/
└── results/   #generated locally and ignored by GitHub

```

## 📄 Citation

If you use this code in your research, please cite:
```bibtex
@article{silva2025creative,
  title = {Sector-based vehicle routing optimization for scalable municipal solid waste collection},
  author = {Sara Meira Moutta},
  journal = {name journal},
  year = {2026},
  note = {Under Review}
}
```

## 📜 License

APACHE License - see LICENSE file for details.


## 👥 Authors & Contact

- **Sara Meira Moutta** (Corresponding Author)
Universidade Estadual de Santa Cruz (UESC)
Programa de Pós-graduação em Modelagem Compuacional UERJ-IPRJ
📧 smoutta@uesc.br

## 🙏 Acknowledgments

This research was supported by:
- Universidade Estadual de Santa Cruz (UESC)
---

**Last Updated**: November 2025  
**Repository Status**: Under active development for publication 
