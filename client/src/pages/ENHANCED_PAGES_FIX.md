# Enhanced Pages - Export Dropdown Fix

The export dropdowns in MeetingsEnhanced, ActionsEnhanced, and CommentsEnhanced currently use:

```javascript
onClick={(e) => {
  const menu = e.currentTarget.nextElementSibling;
  menu.classList.toggle('hidden');
}}
```

This needs to be converted to React state with the useClickOutside hook:

```javascript
const [showExportMenu, setShowExportMenu] = useState(false);
const exportMenuRef = useRef(null);
useClickOutside(exportMenuRef, () => setShowExportMenu(false), showExportMenu);

// Button:
onClick={() => setShowExportMenu(!showExportMenu)}

// Menu div:
<div ref={exportMenuRef} className={`... ${showExportMenu ? '' : 'hidden'}`}>
```

Same fix needed for column selector panels.
