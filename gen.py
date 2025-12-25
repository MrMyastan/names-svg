"""
Tutorial:
    https://developer.mozilla.org/en-US/docs/Web/SVG/Element/text

Usage:
    python3 examples/text.py > examples/text.svg
    chromium examples/text.svg
"""
import sys
from typing import List, Tuple
import svg

from data import Content, FullStyling, LayoutConfig, process_names


def positions_for_remainder(len_remainder, columns: int) -> List[float]:
    return [((columns - len_remainder) / 2) + i for i in range(len_remainder)]

def column_x(i: float, config: LayoutConfig) -> float:
    return (config.canvas_width() / 2) + ((i - ((config.columns - 1) / 2)) * config.name_to_name_horizontal)

def construct_name_group(name: str, index: float, current_y: int, include_roles: bool, config: LayoutConfig) -> svg.G | svg.Text:
    if include_roles:
        name, role = name.split(": ", 1)

    to_return = svg.Text(
            x=column_x(index, config),
            y=current_y,
            text=name,
            class_=["name"],
        )

    if include_roles:
        to_return = svg.G(elements=[
        to_return,
        svg.Text(
            x=column_x(index, config),
            y=current_y + config.name_to_role,
            text=role,
            class_=["role"],
        ),
    ])
        
    return to_return

def process_section(section: List[str], include_roles: bool, current_y: int, config: LayoutConfig) -> Tuple[svg.G, int]:
        
        # * Prepare variables
        columns = config.columns
        canvas_width = config.canvas_width()
        remainder_layouts = [positions_for_remainder(i, columns) for i in range(columns)]

        section = section.copy()
        title = section.pop(0)
        core_block = section[0:len(section) - len(section) % columns]
        remainder = section[len(core_block):]

        # * Construct header SVG
        title_text = svg.Text(
            x=canvas_width/2,
            y=current_y,
            text=title,
            class_=["label"],
        )
        current_y += config.label_to_names

        # * Construct names SVG in core block
        text_columns = [[] for _ in range(columns)]

        for i, name in enumerate(core_block):
            if i % columns == 0 and i != 0:
                current_y += config.name_to_name_jump(include_roles)
            column = i % columns

            to_append = construct_name_group(name, column, current_y, include_roles, config)
            
            text_columns[column].append(to_append)
        
        # * Construct names SVG in remainder line
        remainder_texts = []
        len_remainder = len(remainder)
        if len_remainder > 0:
            current_y += config.name_to_name_jump(include_roles) if len(core_block) > 0 else 0
            layout = remainder_layouts[len_remainder]
            for i, name in enumerate(remainder): 
                to_append = construct_name_group(name, layout[i], current_y, include_roles, config)
            
                if layout[i].is_integer():
                    text_columns[int(layout[i])].append(to_append)
                else:
                    remainder_texts.append(to_append)

        # * Wrap up
        current_y += config.name_to_role if include_roles else 0

        columns_groups = [ svg.G(elements=col) for col in text_columns ]

        return (svg.G(elements=[title_text, *columns_groups, *remainder_texts]), current_y)


def render_svg(content: Content, config: LayoutConfig, text_styling: FullStyling) -> svg.SVG:
    
    current_y = config.initial_y

    # * Construct sections of names with header
    all_elements = []
    for section in content.names:
        svg_section, current_y = process_section(section, content.include_roles, current_y, config)
        all_elements.append(svg_section)
        current_y += config.section_to_section

    # * Construct subtitles
    for i, subtitle in enumerate(content.subtitles):
        current_y += config.section_to_sub1 - config.section_to_section if i == 0 else config.sub1_to_sub2
        subtitle_text = svg.Text(
            x=config.canvas_width()/2,
            y=current_y,
            text=subtitle,
            class_=["sub" + str(i+1)],
        )
        all_elements.append(subtitle_text)

    # * Construct SVG document
    document= svg.SVG(
        width=config.canvas_width(),
        height=current_y + 50,
        elements=[
            svg.Style(
                text=str(text_styling),
            ),            
            *all_elements
        ],
    )
        
    return document



if __name__ == "__main__":
    with open("names.txt", "r") as f:
        file_content = f.read()
    
    try:
        input_content = process_names(file_content)
    except ValueError as e:
        sys.exit(e.args[0])
    
    layout_config = LayoutConfig()

    styles = FullStyling.with_color("#FFFFFF")

    document = render_svg(input_content, layout_config, styles)
    with open("names.svg", "w") as f:
        f.write(str(document))
    