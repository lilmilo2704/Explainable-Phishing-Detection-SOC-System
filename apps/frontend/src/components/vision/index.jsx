export const VuiBox = ({ component: Component = 'div', className = '', children, ...props }) => (
  <Component className={`vui-box ${className}`.trim()} {...props}>
    {children}
  </Component>
);

const typographyElements = {
  h1: 'h1',
  h2: 'h2',
  h3: 'h3',
  h4: 'h4',
  button: 'span',
  caption: 'span',
  body: 'p',
};

export const VuiTypography = ({
  component,
  variant = 'body',
  color = 'white',
  fontWeight = 'regular',
  textGradient = false,
  className = '',
  children,
  ...props
}) => {
  const Component = component || typographyElements[variant] || 'span';
  const classes = [
    'vui-typography',
    `vui-${variant}`,
    `vui-color-${color}`,
    `vui-weight-${fontWeight}`,
    textGradient ? 'vui-text-gradient' : '',
    className,
  ].filter(Boolean).join(' ');

  return <Component className={classes} {...props}>{children}</Component>;
};

export const VuiButton = ({
  color = 'info',
  variant = 'contained',
  size = 'medium',
  iconOnly = false,
  className = '',
  children,
  ...props
}) => (
  <button
    type="button"
    className={`vui-button vui-button-${variant} vui-button-${color} vui-button-${size} ${iconOnly ? 'vui-button-icon' : ''} ${className}`.trim()}
    {...props}
  >
    {children}
  </button>
);

export const VuiInput = ({
  component: Component = 'input',
  icon,
  className = '',
  children,
  ...props
}) => {
  if (!icon) {
    return Component === 'input'
      ? <input className={`vui-input ${className}`.trim()} {...props} />
      : <Component className={`vui-input ${className}`.trim()} {...props}>{children}</Component>;
  }

  return (
    <label className="vui-input-shell">
      {icon}
      {Component === 'input'
        ? <input className={`vui-input vui-input-with-icon ${className}`.trim()} {...props} />
        : <Component className={`vui-input vui-input-with-icon ${className}`.trim()} {...props}>{children}</Component>}
    </label>
  );
};

export const VuiBadge = ({ color = 'info', variant = 'contained', className = '', children }) => (
  <span className={`vui-badge vui-badge-${variant} vui-badge-${color} ${className}`.trim()}>{children}</span>
);

export const GradientBorder = ({ children, className = '' }) => (
  <div className={`gradient-border ${className}`.trim()}>{children}</div>
);

export const DashboardLayout = ({ children }) => (
  <VuiBox className="vision-dashboard-layout">{children}</VuiBox>
);

export const DashboardNavbar = ({ title, context, leading, actions }) => (
  <GradientBorder className="dashboard-navbar-border">
    <VuiBox component="header" className="topbar dashboard-navbar">
      <VuiBox className="topbar-leading">
        {leading}
        <VuiBox>
          <VuiTypography variant="caption" color="text" className="navbar-context">{context}</VuiTypography>
          <VuiTypography component="div" variant="h3" fontWeight="bold" className="topbar-title">
            {title}
          </VuiTypography>
        </VuiBox>
      </VuiBox>
      <VuiBox className="topbar-actions">{actions}</VuiBox>
    </VuiBox>
  </GradientBorder>
);

export const Footer = () => (
  <VuiBox component="footer" className="dashboard-footer">
    <VuiTypography variant="caption" color="text">
      PhishGuard SOC Console
    </VuiTypography>
    <VuiTypography variant="caption" color="text">
      Explainable phishing detection | Analyst-confirmed feedback only
    </VuiTypography>
  </VuiBox>
);

export const MiniStatisticsCard = ({ title, value, icon, color = 'info' }) => (
  <GradientBorder className="statistics-border">
    <VuiBox className="panel metric-card vision-stat-card">
      <VuiBox>
        <VuiTypography variant="caption" color="text" fontWeight="medium" className="card-title">
          {title}
        </VuiTypography>
        <VuiTypography component="p" variant="h2" fontWeight="bold" className="card-value">
          {value}
        </VuiTypography>
      </VuiBox>
      <VuiBox className={`metric-icon metric-icon-${color}`}>{icon}</VuiBox>
    </VuiBox>
  </GradientBorder>
);
