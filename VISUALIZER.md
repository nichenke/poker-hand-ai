# GTO Analysis Visualizer

A web-based visualization tool for poker hand analysis results, featuring a ChatGPT-like interface.

## Features

- **Clean Web Interface**: Modern, responsive design similar to ChatGPT
- **Analysis Overview**: Grid view of all processed hands with key metadata
- **Detailed Analysis View**: Comprehensive display of:
  - Hand history with syntax highlighting
  - GTO+ solver results (ranges, frequencies, EV analysis)
  - AI strategic analysis with markdown formatting
- **Interactive Elements**: Copy hand histories, responsive layout
- **Real-time Updates**: Automatically detects new analysis files

## Quick Start

```bash
# Start the visualizer
make visualize

# Or run directly
python visualizer.py
```

Then open your browser to: http://localhost:8081

## Interface Overview

### Main Page
- **Analysis Cards**: Each processed hand displayed as a card
- **Metadata**: Hand ID, stakes, processing timestamp
- **Quick Access**: Click "View Analysis" to see detailed results

### Analysis View
- **Hand History**: Formatted poker hand with action highlighting
- **Solver Results**: 
  - **Ranges**: Position-based hand ranges in an easy-to-read format
  - **Frequencies**: Action frequencies as percentages
  - **EV Analysis**: Expected value calculations with color coding
- **AI Analysis**: Strategic insights formatted as markdown with sections for:
  - Strategic assessment
  - GTO deviations
  - EV impact analysis
  - Improvement suggestions
  - Learning points

## Technical Details

### Dependencies
- **Flask**: Web framework
- **Markdown**: AI analysis formatting
- **Pathlib**: File system operations

### File Structure
```
static/
├── style.css    # Modern CSS with card-based design
└── script.js    # Interactive functionality

templates/
├── base.html    # Base template with navigation
├── index.html   # Analysis list page
└── analysis.html # Detailed analysis view
```

### API Endpoints
- `GET /` - Main analysis list
- `GET /analysis/<filename>` - View specific analysis
- `GET /api/analyses` - JSON API for analysis metadata

## Customization

### Styling
Edit `static/style.css` to customize the interface:
- Color scheme variables in `:root`
- Card layouts and grid systems
- Typography and spacing

### Templates
Modify templates in `templates/` folder:
- `base.html` - Navigation and overall layout
- `index.html` - Analysis list customization
- `analysis.html` - Detailed view formatting

### Data Processing
The visualizer includes formatting functions for:
- Hand history syntax highlighting
- Range display optimization
- Frequency percentage calculations
- EV analysis color coding

## Integration

The visualizer automatically reads from the `exports/` folder where the main GTO Assistant saves analysis files. No configuration needed - just run analyses and view them in the web interface.

### Workflow
1. Process hands with: `make run`
2. Start visualizer with: `make visualize`
3. View results at: http://localhost:8081
4. New analyses appear automatically

## Browser Compatibility

Tested on:
- Chrome/Chromium
- Firefox
- Safari
- Edge

Responsive design works on mobile devices and tablets.
