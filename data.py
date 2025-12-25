from dataclasses import dataclass, field, fields
import html
from textwrap import dedent
from typing import Dict, List, Self

@dataclass
class LayoutConfig:
    columns: int = 5
    name_to_name_vertical: int = 50
    name_to_name_horizontal: int = 220
    label_to_names: int = 50
    section_to_section: int = 80
    name_to_role: int = 20
    section_to_sub1: int = 60
    sub1_to_sub2: int = 30
    initial_y: int = 75

    def name_to_name_jump(self, include_roles: bool) -> int:
        return self.name_to_name_vertical + (self.name_to_role if include_roles else 0)
    
    def canvas_width(self) -> float:
        return (self.columns + 0.5) * self.name_to_name_horizontal

    # TODO: error if not has?
    def set_value(self, key:str, val:int):
        if hasattr(self, key):
            setattr(self, key, val)

    def get_value(self, key:str):
        if hasattr(self, key):
            return getattr(self, key)
        return None
        
    def get_all_keys_and_values(self) -> Dict[str, int]:
        output = {}
        for field in fields(self):
            output[field.name] = self.get_value(field.name)
        return output
    
    def get_all_defaults(self) -> Dict[str, int]:
        output = {}
        for field in fields(self):
            output[field.name] = field.default
        return output
    
@dataclass
class TextStyling:
    font_size: str
    fill: str
    font_family: str
    font_weight: str
    font_style: str

    def __str__(self):
        return dedent(f"""
            font-family: '{self.font_family}';
            font-size: {self.font_size};
            fill: {self.fill};
            font-weight: {self.font_weight};
            font-style: {self.font_style};
        """)
    
    @classmethod
    def name_defaults(cls) -> Self:
        return cls(
            font_size="27px",
            fill="white",
            font_family="Bodoni 72 Smallcaps",
            font_weight="normal",
            font_style="normal",
        )
    
    @classmethod
    def role_defaults(cls) -> Self:
        return cls(
            font_size="18px",
            fill="white",
            font_family="Bodoni 72 Smallcaps",
            font_weight="normal",
            font_style="italic",
        )
    
    @classmethod
    def label_defaults(cls) -> Self:
        return cls(
            font_size="64px",
            fill="white",
            font_family="Brush Script MT",
            font_weight="bold",
            font_style="italic",
        )
    
    @classmethod
    def sub1_defaults(cls) -> Self:
        return cls(
            font_size="48px",
            fill="white",
            font_family="Brush Script MT",
            font_weight="normal",
            font_style="normal",
        )
    
    @classmethod
    def sub2_defaults(cls) -> Self:
        return cls(
            font_size="24px",
            fill="white",
            font_family="Bodoni 72 Smallcaps",
            font_weight="normal",
            font_style="normal",
        )
    
    def update_from_other(self, other: Self):
        self.fill = other.fill
        self.font_family = other.font_family
        self.font_size = other.font_size
        self.font_style = other.font_style
        self.font_weight = other.font_weight


@dataclass
class FullStyling:
    name_style: TextStyling = field(default_factory=TextStyling.name_defaults)
    role_style: TextStyling = field(default_factory=TextStyling.role_defaults)
    label_style: TextStyling = field(default_factory=TextStyling.label_defaults)
    sub1_style: TextStyling = field(default_factory=TextStyling.sub1_defaults)
    sub2_style: TextStyling = field(default_factory=TextStyling.sub2_defaults)

    @classmethod
    def with_color(cls, color: str) -> Self:
        name_style = TextStyling.name_defaults()
        name_style.fill = color
        role_style = TextStyling.role_defaults()
        role_style.fill = color
        label_style = TextStyling.label_defaults()
        label_style.fill = color
        sub1_style = TextStyling.sub1_defaults()
        sub1_style.fill = color
        sub2_style = TextStyling.sub2_defaults()
        sub2_style.fill = color
        return cls(
            name_style=name_style,
            role_style=role_style,
            label_style=label_style,
            sub1_style=sub1_style,
            sub2_style=sub2_style,
        )

    def __str__(self):
        return dedent(f"""
            .name {{ {self.name_style} }}
            .role {{ {self.role_style} }}
            .label {{ {self.label_style} }}
            .sub1 {{ {self.sub1_style} }}
            .sub2 {{ {self.sub2_style} }}
            text {{ text-anchor: middle; }}
        """)

@dataclass
class Content:
    names: List[List[str]]
    subtitles: List[str]
    include_roles: bool

def process_names(names_str: str) -> Content:
    
    names_str = html.escape(names_str)

    names = [section.strip() for section in names_str.split("\n\n") if section.strip()]
    names = [section.split("\n") for section in names]

    subtitles = []
    if names[-1][0].startswith("Subs: "):
        subtitles = names.pop()
        subtitles[0] = subtitles[0].replace("Subs: ", "")
        if len(subtitles) > 2:
            raise ValueError("Subtitles section can only have one line after the 'Subs: ' line.")

    include_roles = False
    if ": " in names[0][1]:
        include_roles = True

    for section in names:
        if not all(include_roles == (": " in name) for name in section[1:]):
            raise ValueError(f"Some names include roles and some do not in the section '{section[0]}'. Please make them consistent.")
    return Content(names, subtitles, include_roles)
