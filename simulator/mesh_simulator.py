import random
from typing import Dict, List

class DynamicMeshSimulator:
    def __init__(self, node_count: int = 20):
        self.node_count = node_count
        self.gateway_id = 'GATEWAY-001'
        self.node_status = {f'NODE-{i:03d}': True for i in range(1, node_count + 1)}

    def set_node_status(self, node_id: str, is_online: bool):
        self.node_status[node_id] = is_online

    def get_route_to_gateway(self, node_id: str) -> Dict:
        if not self.node_status.get(node_id, False):
            return {'node_id': node_id, 'route': [], 'hop_count': -1, 'status': 'OFFLINE'}
        
        idx = int(node_id.split('-')[1])
        if idx <= 4:
            route = [node_id, self.gateway_id]
            hop_count = 1
        elif idx <= 8:
            parent = f'NODE-{(idx % 4) + 1:03d}'
            route = [node_id, parent, self.gateway_id]
            hop_count = 2
        elif idx <= 14:
            hop1 = f'NODE-{(idx - 4):03d}'
            hop2 = f'NODE-{((idx - 4) % 4) + 1:03d}'
            route = [node_id, hop1, hop2, self.gateway_id]
            hop_count = 3
        else:
            hop1 = f'NODE-{(idx - 5):03d}'
            hop2 = f'NODE-{(idx - 10):03d}'
            route = [node_id, hop1, hop2, self.gateway_id]
            hop_count = 3
        
        return {
            'node_id': node_id,
            'route': route,
            'hop_count': hop_count,
            'parent': route[1] if len(route) > 1 else self.gateway_id,
            'signal_strength': -50 - (hop_count * 8) + random.randint(-2, 2),
            'status': 'ONLINE'
        }
