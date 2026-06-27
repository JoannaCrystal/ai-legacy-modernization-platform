import { useMemo } from 'react';
import {
  Background,
  Controls,
  Handle,
  MiniMap,
  Position,
  ReactFlow,
  type Edge,
  type Node,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';

import type { ArchitectureSummary } from '../../types/api';

interface ArchitectureDiagramProps {
  architectureSummary: ArchitectureSummary;
}

interface ComponentNodeData {
  label: string;
  nodeType: 'component' | 'class';
}

function ComponentNode({ data }: { data: ComponentNodeData }) {
  const isComponent = data.nodeType === 'component';

  return (
    <Box
      sx={{
        px: 2,
        py: 1,
        minWidth: isComponent ? 220 : 180,
        borderRadius: 2,
        bgcolor: isComponent ? 'primary.main' : 'background.paper',
        color: isComponent ? 'primary.contrastText' : 'text.primary',
        border: isComponent ? 'none' : '1px solid',
        borderColor: 'divider',
        boxShadow: 2,
        fontWeight: isComponent ? 700 : 500,
        fontSize: isComponent ? '0.95rem' : '0.85rem',
        textAlign: 'center',
      }}
    >
      {!isComponent && (
        <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
      )}
      {data.label}
      {isComponent && (
        <Handle
          type="source"
          position={Position.Bottom}
          style={{ opacity: 0 }}
        />
      )}
    </Box>
  );
}

const nodeTypes = {
  componentNode: ComponentNode,
};

function buildDiagram(architectureSummary: ArchitectureSummary): {
  nodes: Node[];
  edges: Edge[];
} {
  const components = architectureSummary.components ?? [];
  const nodes: Node[] = [];
  const edges: Edge[] = [];

  let yOffset = 0;

  components.forEach((component, componentIndex) => {
    const componentId = `component-${componentIndex}`;
    const componentY = yOffset;

    nodes.push({
      id: componentId,
      type: 'componentNode',
      position: { x: 250, y: componentY },
      data: {
        label: component.name,
        nodeType: 'component',
      },
    });

    component.classes.forEach((className, classIndex) => {
      const classId = `class-${componentIndex}-${classIndex}`;
      const classY = componentY + 90 + classIndex * 70;

      nodes.push({
        id: classId,
        type: 'componentNode',
        position: { x: 250, y: classY },
        data: {
          label: className,
          nodeType: 'class',
        },
      });

      edges.push({
        id: `edge-${componentId}-${classId}`,
        source: componentId,
        target: classId,
        type: 'smoothstep',
        style: { stroke: '#64748b' },
      });
    });

    yOffset = componentY + 90 + component.classes.length * 70 + 80;
  });

  return { nodes, edges };
}

export default function ArchitectureDiagram({
  architectureSummary,
}: ArchitectureDiagramProps) {
  const { nodes, edges } = useMemo(
    () => buildDiagram(architectureSummary),
    [architectureSummary],
  );

  if (nodes.length === 0) {
    return (
      <Typography color="text.secondary">
        No architecture diagram available for this project.
      </Typography>
    );
  }

  return (
    <Paper sx={{ height: 480, overflow: 'hidden' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#e2e8f0" gap={16} />
        <Controls showInteractive={false} />
        <MiniMap pannable zoomable />
      </ReactFlow>
    </Paper>
  );
}
