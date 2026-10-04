import { useState } from 'react';
import { LayoutChangeEvent, View } from 'react-native';
import Svg, { Circle, Line, Polyline, Rect } from 'react-native-svg';
import { color } from '../theme';

type Band = { from: number; to: number; fill: string };
type Rule = { at: number; dashed?: boolean; stroke?: string };

// Small, dependency-free line chart. Data series in brand violet at 2px.
export function LineChart({
  values,
  min,
  max,
  height = 110,
  bands = [],
  rules = [],
  baseline,
  highlightIndex,
  highlightColor = color.riskWarning,
}: {
  values: number[];
  min: number;
  max: number;
  height?: number;
  bands?: Band[];
  rules?: Rule[];
  baseline?: number;
  highlightIndex?: number;
  highlightColor?: string;
}) {
  const [width, setWidth] = useState(0);
  const onLayout = (e: LayoutChangeEvent) => setWidth(e.nativeEvent.layout.width);
  const pad = 6;
  const y = (v: number) => pad + (1 - (v - min) / (max - min)) * (height - pad * 2);
  const x = (i: number) => pad + (i / (values.length - 1)) * (width - pad * 2);
  const points = values.map((v, i) => `${x(i)},${y(v)}`).join(' ');

  return (
    <View onLayout={onLayout} style={{ height }}>
      {width > 0 && (
        <Svg width={width} height={height}>
          {bands.map((b) => (
            <Rect key={`${b.from}-${b.to}`} x={0} width={width} y={y(Math.min(b.to, max))} height={y(Math.max(b.from, min)) - y(Math.min(b.to, max))} fill={b.fill} />
          ))}
          {rules.map((r) => (
            <Line key={r.at} x1={0} x2={width} y1={y(r.at)} y2={y(r.at)} stroke={r.stroke ?? color.line} strokeWidth={1} strokeDasharray={r.dashed ? '4 4' : undefined} />
          ))}
          {baseline !== undefined && (
            <Line x1={0} x2={width} y1={y(baseline)} y2={y(baseline)} stroke={color.inkMuted} strokeWidth={1.5} strokeDasharray="4 4" />
          )}
          <Polyline points={points} fill="none" stroke={color.brand} strokeWidth={2.5} strokeLinejoin="round" strokeLinecap="round" />
          {highlightIndex !== undefined && (
            <Circle cx={x(highlightIndex)} cy={y(values[highlightIndex])} r={4.5} fill={color.surface} stroke={highlightColor} strokeWidth={2} />
          )}
        </Svg>
      )}
    </View>
  );
}
