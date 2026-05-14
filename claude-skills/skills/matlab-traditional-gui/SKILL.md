---
name: matlab-traditional-gui
description: Build, refactor, or review MATLAB traditional GUI code using figure, uicontrol, uipanel, normalized layout, SizeChangedFcn, UserData, and nested callbacks. Use for R2025b-compatible GUI work, especially when avoiding uifigure due to Windows text scaling issues.
when_to_use: Use when the task involves MATLAB .m GUI files, traditional figure/uicontrol UI, responsive layout, font scaling, callback wiring, gobjects handle arrays, UserData state management, or debugging window drift, flicker, SizeChangedFcn, and resize problems.
argument-hint: "[requirements-or-m-file]"
disable-model-invocation: true
---

# MATLAB Traditional GUI Development

Use this skill to design, implement, refactor, or review MATLAB traditional GUIs built with `figure`, `uicontrol`, and `uipanel`.

Default to the traditional `figure` + `uicontrol` approach when the user explicitly asks for it, when the project already uses it, or when `uifigure` causes Windows text scaling/layout problems.

## Core rules

- Use `figure`, `uicontrol`, and `uipanel` rather than `uifigure` unless the user explicitly requests App Designer-style UI.
- Use pixel units only for the top-level `figure` design size.
- Use `normalized` units for panels and child controls so the layout scales with the window.
- Keep layout geometry and font scaling separate: resize should adjust fonts, not rewrite the window position.
- Store shared handles and state in `fig.UserData`.
- Use nested callback functions inside the main UI function so callbacks can access `fig` through closure capture.
- Use `gobjects(N, 1)` for graphics handle preallocation; do not use `zeros()` for handle arrays.
- Do not use global variables for GUI state.

## Window creation pattern

Create the window hidden first, then build controls, then reveal it.

```matlab
fig = figure('Name', '窗口标题', ...
             'NumberTitle', 'off', ...
             'Units', 'pixels', ...
             'Position', [100 100 designW designH], ...
             'Visible', 'off', ...
             'Resize', 'on', ...
             'MenuBar', 'none', ...
             'ToolBar', 'none', ...
             'Color', [0.94 0.94 0.94]);
```

Use a design baseline:

```matlab
designW = 480;
designH = 720;
baseFont = 10;
```

## Layout pattern

Use normalized coordinates for panels and controls.

```matlab
p1 = uipanel(fig, 'Title', '面板标题', ...
             'Units', 'normalized', ...
             'Position', [0.04 0.50 0.92 0.40], ...
             'FontSize', baseFont);
```

Interpret `Position` as `[left bottom width height]`, where all values are proportions in the parent container.

Keep at least `0.02` normalized vertical spacing between panels when the title area may collide with child controls.

## Construction order

Follow this order exactly:

1. Create `fig` with `'Visible', 'off'`.
2. Create all panels and controls.
3. Collect handles whose fonts should scale into `all_text`.
4. Build the `UserData` struct.
5. Assign `fig.UserData = ud`.
6. Set `fig.Visible = 'on'`.
7. Call `movegui(fig, 'center')`.
8. Assign `fig.SizeChangedFcn = @on_resize`.
9. Manually call `on_resize(fig, [])` once.

Bind `SizeChangedFcn` after `movegui`; otherwise `movegui` can trigger resize logic before the layout is stable.

## Resize pattern

Use a re-entry lock. Scale font sizes from the current figure height.

```matlab
function on_resize(~, ~)
    ud = fig.UserData;
    if isempty(ud) || ud.in_resize
        return;
    end

    ud.in_resize = true;
    fig.UserData = ud;

    pos = fig.Position;
    scale = max(pos(4) / ud.designH, 0.7);
    newFont = max(round(ud.baseFont * scale), 7);
    btnFont = max(round(14 * scale), 10);

    for h = ud.all_text'
        if isvalid(h)
            set(h, 'FontSize', newFont);
        end
    end

    if isfield(ud, 'h_btn') && isvalid(ud.h_btn)
        set(ud.h_btn, 'FontSize', btnFont);
    end

    ud2 = fig.UserData;
    ud2.in_resize = false;
    fig.UserData = ud2;
end
```

Never assign `fig.Position = pos` inside `on_resize`; it can create a Windows asynchronous resize feedback loop causing drift or flicker.

Do not include `uipanel` objects in `all_text`; changing panel `FontSize` during resize can trigger internal layout recalculation and resize feedback.

## Handle and state pattern

Preallocate graphics handles with `gobjects`.

```matlab
h_edit = gobjects(6, 1);
for i = 1:6
    h_edit(i) = uicontrol(...);
end
```

Store shared state and handles in `fig.UserData`.

```matlab
ud = struct();
ud.h_edit     = h_edit;
ud.h_btn      = h_btn;
ud.h_status   = h_status;
ud.baseFont   = baseFont;
ud.designH    = designH;
ud.all_text   = all_text;
ud.in_resize  = false;
fig.UserData  = ud;
```

Callbacks should read state with `ud = fig.UserData` and write back with `fig.UserData = ud` when state changes.

## Callback pattern

Place callbacks as nested functions inside the main UI function.

```matlab
function my_ui()
    fig = figure(...);

    function run_callback(~, ~)
        ud = fig.UserData;
        % callback logic
    end
end
```

For long-running actions, disable the trigger button, show status, call `drawnow`, use `try/catch`, and re-enable the button at the end.

```matlab
function run_callback(~, ~)
    ud = fig.UserData;
    set(ud.h_btn, 'Enable', 'off');
    set(ud.h_status, 'String', '正在运行...', ...
        'ForegroundColor', [0.3 0.3 0.3]);
    drawnow;

    try
        % core logic here
        set(ud.h_status, 'String', '完成', ...
            'ForegroundColor', [0 0.5 0]);
    catch ME
        set(ud.h_status, 'String', sprintf('出错: %s', ME.message), ...
            'ForegroundColor', [0.8 0 0]);
    end

    set(ud.h_btn, 'Enable', 'on');
end
```

## Validation requirements

When generating or reviewing GUI code, check for:

- `SizeChangedFcn` bound before `UserData` is initialized.
- `SizeChangedFcn` bound before `movegui`.
- `fig.Position` assignment inside resize callbacks.
- `uipanel` included in the font-scaling handle list.
- `zeros()` used for graphics handle preallocation.
- Missing `in_resize` re-entry lock.
- Callback state stored in globals instead of `fig.UserData`.
- Long-running callbacks that do not disable the trigger button.
- Status labels that do not report success or failure.
- Numeric UI inputs that are not validated before use.
- Ratios that must be integers but are not checked, such as `fsFac/fpFac` before `repelem`.

## Troubleshooting map

| Symptom | Likely cause | Fix |
|---|---|---|
| Window drifts upward during resize | `on_resize` assigns `fig.Position` | Remove position reassignment; only scale fonts |
| Window flickers during resize | Re-entrant resize/layout feedback | Add `in_resize` lock and avoid panel font changes |
| Startup error says `fig` is undefined | Resize callback fires before closure/state is ready | Use `Visible='off'`; bind callback after construction |
| `UserData` is empty in callback | Callback bound before `fig.UserData` assignment | Assign `UserData` before binding callbacks that depend on it |
| Panel title overlaps controls | Panels are too close | Add at least `0.02` normalized spacing |
| `repelem` errors | Segment count is non-integer | Validate integer ratio before calling `repelem` |
| Graphics handle array becomes double | Used `zeros()` for handles | Use `gobjects()` |

## Full skeleton

```matlab
function my_ui()
    designW = 480;
    designH = 720;
    baseFont = 10;

    fig = figure('Name', '标题', ...
                 'NumberTitle', 'off', ...
                 'Units', 'pixels', ...
                 'Position', [100 100 designW designH], ...
                 'Visible', 'off', ...
                 'Resize', 'on', ...
                 'MenuBar', 'none', ...
                 'ToolBar', 'none', ...
                 'Color', [0.94 0.94 0.94]);

    p1 = uipanel(fig, 'Title', '面板', ...
                 'Units', 'normalized', ...
                 'Position', [0.04 0.50 0.92 0.40], ...
                 'FontSize', baseFont);

    h_status = uicontrol(fig, 'Style', 'text', ...
                         'Units', 'normalized', ...
                         'Position', [0.04 0.02 0.92 0.04], ...
                         'String', '就绪', ...
                         'HorizontalAlignment', 'left', ...
                         'FontSize', baseFont);

    h_btn = uicontrol(fig, 'Style', 'pushbutton', ...
                      'Units', 'normalized', ...
                      'Position', [0.25 0.08 0.50 0.06], ...
                      'String', '运行', ...
                      'FontSize', 14, ...
                      'Callback', @run_callback);

    all_text = [findobj(fig, 'Style', 'text'); h_status];

    ud = struct();
    ud.h_btn = h_btn;
    ud.h_status = h_status;
    ud.baseFont = baseFont;
    ud.designH = designH;
    ud.all_text = all_text;
    ud.in_resize = false;
    fig.UserData = ud;

    fig.Visible = 'on';
    movegui(fig, 'center');
    fig.SizeChangedFcn = @on_resize;
    on_resize(fig, []);

    function run_callback(~, ~)
        ud = fig.UserData;
        set(ud.h_btn, 'Enable', 'off');
        set(ud.h_status, 'String', '正在运行...', ...
            'ForegroundColor', [0.3 0.3 0.3]);
        drawnow;

        try
            % TODO: core logic
            set(ud.h_status, 'String', '完成', ...
                'ForegroundColor', [0 0.5 0]);
        catch ME
            set(ud.h_status, 'String', sprintf('出错: %s', ME.message), ...
                'ForegroundColor', [0.8 0 0]);
        end

        set(ud.h_btn, 'Enable', 'on');
    end

    function on_resize(~, ~)
        ud = fig.UserData;
        if isempty(ud) || ud.in_resize
            return;
        end

        ud.in_resize = true;
        fig.UserData = ud;

        pos = fig.Position;
        scale = max(pos(4) / ud.designH, 0.7);
        newFont = max(round(ud.baseFont * scale), 7);
        btnFont = max(round(14 * scale), 10);

        for h = ud.all_text'
            if isvalid(h)
                set(h, 'FontSize', newFont);
            end
        end

        if isvalid(ud.h_btn)
            set(ud.h_btn, 'FontSize', btnFont);
        end

        ud2 = fig.UserData;
        ud2.in_resize = false;
        fig.UserData = ud2;
    end
end
```

## Output expectations

When this skill is used:

- For code generation, produce a complete `.m` function unless the user asks for a patch only.
- For code review, identify violations of the rules above before suggesting stylistic improvements.
- For debugging, map the symptom to the troubleshooting table and propose the smallest safe change first.
- For refactoring, preserve existing behavior unless the user explicitly asks for redesign.