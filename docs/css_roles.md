# CSS Roles Documentation

This document outlines how CSS roles are defined in the Anvil app, organized by component type. The theme implements Material Design 3 look and feel.

## General Layout Roles

### Panel Column Roles
- Default panel columns have padding-bottom and negative margin to prevent shadow cutoff
```css
.anvil-panel-col {
  padding-bottom: 10px;
  margin-bottom: -10px;
}
```

### Spacing Roles
- Four levels of spacing (none, small, medium, large) for both above and below:
```css
.anvil-spacing-above-none { margin-top: 0px; }
.anvil-spacing-above-small { margin-top: 4px; }
.anvil-spacing-above-medium { margin-top: 8px; }
.anvil-spacing-above-large { margin-top: 16px; }
```

### Column Padding Roles
- Five levels of column padding (tiny to huge):
```css
.col-padding.col-padding-tiny { padding: 0 2px; }
.col-padding.col-padding-small { padding: 0 4px; }
.col-padding.col-padding-medium { padding: 0 8px; }
.col-padding.col-padding-large { padding: 0 12px; }
.col-padding.col-padding-huge { padding: 0 20px; }
```

## Typography Roles

### Text Roles
- `display`: Large display text (57px)
- `headline`: Section headers (32px)
- `title`: Subsection titles (22px)
- `body`: Regular text (14px)
- `input-prompt`: Form input labels (16px)

Example:
```css
.anvil-role-display {
  font-size: 57px;
  line-height: 64px;
  font-weight: 400;
}
```

## Component-Specific Roles

### Button Roles

1. **Default Button**
- Base styling with rounded corners and no background
```css
.btn {
  border-radius: 100px;
  font-size: 14px;
  font-weight: 500;
  padding: 10px 24px;
}
```

2. **Outlined Button** (`outlined-button`)
- Transparent background with colored border
```css
.anvil-role-outlined-button > .btn {
  color: %color:Primary%;
  border: solid 1px %color:Outline%;
}
```

3. **Filled Button** (`filled-button`)
- Solid background color
```css
.anvil-role-filled-button > .btn {
  background-color: %color:Primary%;
  color: %color:On Primary%;
}
```

4. **Elevated Button** (`elevated-button`)
- Button with shadow effect
```css
.anvil-role-elevated-button > .btn {
  background-color: %color:Surface%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}
```

5. **Tonal Button** (`tonal-button`)
- Secondary color scheme
```css
.anvil-role-tonal-button > .btn {
  color: %color:On Secondary Container%;
  background-color: %color:Secondary Container%;
}
```

### Card Roles

1. **Outlined Card** (`outlined-card`)
```css
.anvil-role-outlined-card {
  border-radius: 12px;
  background-color: %color:Surface%;
  border: solid 1px %color:Outline%;
  padding: 15px;
}
```

2. **Elevated Card** (`elevated-card`)
```css
.anvil-role-elevated-card {
  border-radius: 12px;
  background-color: %color:Surface%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}
```

3. **Tonal Card** (`tonal-card`)
```css
.anvil-role-tonal-card {
  border-radius: 12px;
  background-color: %color:Surface Variant%;
}
```

### Input Field Roles

1. **Default Input**
- Base styling for text inputs
```css
input.anvil-component {
  font-size: 16px;
  line-height: 1.5;
  border-radius: 4px 4px 0 0;
  background-color: %color:Surface Variant%;
}
```

2. **Outlined Input** (`outlined`)
```css
input.anvil-component.anvil-role-outlined {
  background-color: transparent;
  border: 1px solid %color:Outline%;
  border-radius: 4px;
}
```

### Custom Application Roles

1. **Task Parser Title** (`task-parser-title`)
```css
.anvil-role-task-parser-title > .label-text {
  font-size: 24px;
  font-weight: 500;
  color: #1F2937;
}
```

2. **Task Input** (`task-input`)
```css
textarea.anvil-component.anvil-role-task-input {
  padding: 12px;
  background-color: #F8F9FA;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
}
```

3. **Process Button** (`process-button`)
```css
.anvil-role-process-button .btn {
  background-color: #374151;
  color: #FFFFFF;
  border-radius: 12px;
}
```

### Loading States

1. **Skeleton Loading** (`skeleton`)
```css
.anvil-role-skeleton {
  animation: skeleton-loading 1s linear infinite alternate;
  height: 30px;
  border-radius: 12px;
}
```

## Navigation Roles

### Left Navigation
- Styling for sidebar navigation items
```css
.left-nav a {
  color: %color:On Surface Variant%;
  margin: 0 -8px;
  padding: 4px 16px;
  border-radius: 100px;
}
```

### App Bar
- Top navigation bar styling
```css
.app-bar {
  min-height: 56px;
  padding: 0 16px 0 72px;
  background-color: %color:Surface%;
}
```

## Usage Examples

1. **Button with Multiple Roles**
```yaml
- type: Button
  properties:
    role: [filled-button, process-button]
```

2. **Card with Loading State**
```yaml
- type: ColumnPanel
  properties:
    role: [outlined-card, skeleton]
```

3. **Text Input with Outline**
```yaml
- type: TextBox
  properties:
    role: [outlined, task-input]
```

## Best Practices

1. **Role Combinations**
- Combine roles to achieve desired styling
- Ensure roles don't conflict with each other
- Remove skeleton roles after loading completes

2. **Typography**
- Use appropriate text roles for hierarchy
- Maintain consistent font sizes
- Follow Material Design guidelines

3. **Component States**
- Handle hover, focus, and active states
- Consider disabled states
- Implement loading states when appropriate

4. **Accessibility**
- Maintain sufficient color contrast
- Use appropriate text sizes
- Ensure interactive elements are clearly visible
