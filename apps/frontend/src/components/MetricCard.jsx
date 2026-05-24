import { MiniStatisticsCard } from './vision';

const MetricCard = ({ title, value, icon, color = "var(--accent)" }) => {
  const tone = color.includes('danger') || color.includes('critical') ? 'error' : color.includes('warning') ? 'warning' : color.includes('success') ? 'success' : 'info';
  return <MiniStatisticsCard title={title} value={value} icon={icon} color={tone} />;
};

export default MetricCard;
