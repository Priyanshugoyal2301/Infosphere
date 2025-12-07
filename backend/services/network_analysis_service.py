"""
Network Analysis Service
Track citation networks and detect circular reporting
"""

import networkx as nx
from typing import Dict, List, Set
from collections import defaultdict
import json
from pathlib import Path


class NetworkAnalyzer:
    """Analyze citation networks and detect circular reporting"""
    
    def __init__(self):
        self.citation_graph = nx.DiGraph()
        self.trust_scores = {}
        self.db_path = Path("data/citation_network.json")
        self.db_path.parent.mkdir(exist_ok=True)
        self._load_network()
    
    def _load_network(self):
        """Load citation network from disk"""
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                data = json.load(f)
                self.citation_graph = nx.node_link_graph(data.get("graph", {}))
                self.trust_scores = data.get("trust_scores", {})
    
    def _save_network(self):
        """Save citation network to disk"""
        data = {
            "graph": nx.node_link_data(self.citation_graph),
            "trust_scores": self.trust_scores
        }
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_citation(self, citing_source: str, cited_source: str, article_url: str):
        """Add a citation relationship"""
        self.citation_graph.add_edge(citing_source, cited_source, url=article_url)
        
        # Initialize trust scores if needed
        if citing_source not in self.trust_scores:
            self.trust_scores[citing_source] = 0.5  # Neutral start
        if cited_source not in self.trust_scores:
            self.trust_scores[cited_source] = 0.5
        
        self._save_network()
    
    def detect_circular_reporting(self, source: str, max_depth: int = 3) -> Dict:
        """Detect if a source is part of circular citation"""
        if source not in self.citation_graph:
            return {"circular": False, "cycle": []}
        
        try:
            # Find all cycles involving this source
            cycles = list(nx.simple_cycles(self.citation_graph))
            source_cycles = [cycle for cycle in cycles if source in cycle]
            
            if source_cycles:
                return {
                    "circular": True,
                    "cycles": source_cycles,
                    "cycle_count": len(source_cycles),
                    "warning": "Source participates in circular reporting"
                }
            
            return {"circular": False, "cycle": []}
        except:
            return {"circular": False, "cycle": []}
    
    def calculate_trust_score(self, source: str) -> float:
        """Calculate trust score based on citation patterns"""
        if source not in self.citation_graph:
            return 0.5  # Neutral for unknown sources
        
        score = 0.5  # Base score
        
        # Factor 1: Who cites this source (in-degree)
        in_edges = list(self.citation_graph.in_edges(source))
        citing_sources = [edge[0] for edge in in_edges]
        
        if citing_sources:
            # If cited by high-trust sources, increase score
            avg_citer_trust = sum(self.trust_scores.get(s, 0.5) for s in citing_sources) / len(citing_sources)
            score += (avg_citer_trust - 0.5) * 0.3
        
        # Factor 2: Who does this source cite (out-degree)
        out_edges = list(self.citation_graph.out_edges(source))
        
        # Factor 3: Circular reporting penalty
        circular_info = self.detect_circular_reporting(source)
        if circular_info["circular"]:
            score -= 0.2 * len(circular_info.get("cycles", []))
        
        # Factor 4: Citation diversity
        cited_sources = [edge[1] for edge in out_edges]
        if len(set(cited_sources)) > 5:  # Cites diverse sources
            score += 0.1
        
        # Clamp between 0 and 1
        score = max(0.0, min(1.0, score))
        
        # Update stored score
        self.trust_scores[source] = score
        self._save_network()
        
        return score
    
    def get_citation_network(self, source: str, depth: int = 2) -> Dict:
        """Get citation network for a source"""
        if source not in self.citation_graph:
            return {"nodes": [], "edges": []}
        
        # Get subgraph within depth
        nodes = set([source])
        for _ in range(depth):
            new_nodes = set()
            for node in nodes:
                # Add sources this cites
                new_nodes.update([edge[1] for edge in self.citation_graph.out_edges(node)])
                # Add sources that cite this
                new_nodes.update([edge[0] for edge in self.citation_graph.in_edges(node)])
            nodes.update(new_nodes)
        
        subgraph = self.citation_graph.subgraph(nodes)
        
        return {
            "nodes": [
                {
                    "id": node,
                    "trust_score": self.trust_scores.get(node, 0.5),
                    "in_degree": self.citation_graph.in_degree(node),
                    "out_degree": self.citation_graph.out_degree(node)
                }
                for node in subgraph.nodes()
            ],
            "edges": [
                {"source": edge[0], "target": edge[1]}
                for edge in subgraph.edges()
            ]
        }
    
    def identify_echo_chambers(self) -> List[Set[str]]:
        """Identify groups of sources that only cite each other"""
        try:
            # Find strongly connected components
            components = list(nx.strongly_connected_components(self.citation_graph))
            
            # Filter out single-node components
            echo_chambers = [comp for comp in components if len(comp) > 2]
            
            return echo_chambers
        except:
            return []


# Global instance
network_analyzer = NetworkAnalyzer()
