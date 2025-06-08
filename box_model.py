from parsers import parse_expression, get_param, parse_gap

class BoxModel:
    """
    A class representing a box model for positioning and aligning rectangular elements.
    
    The BoxModel handles positioning, movement, and alignment of boxes based on their
    anchors and dimensions. It supports operations like moving, aligning, placing beside,
    and placing inside other boxes.
    
    Attributes:
        POSITIONS (dict): A dictionary mapping position names to their relative values (0-1).
        owner: The owner of this box model (usually a parent element).
        _x (float): The x-coordinate of the box's position.
        _y (float): The y-coordinate of the box's position.
        _width (float): The width of the box.
        _height (float): The height of the box.
        _anchor_x (str): The horizontal anchor point ('left', 'center', 'right', or numeric).
        _anchor_y (str): The vertical anchor point ('top', 'center', 'bottom', or numeric).
        _dx (float): Accumulated horizontal movement since last notification.
        _dy (float): Accumulated vertical movement since last notification.
        auto_move (bool): Whether to automatically notify owner on movement.
    """
    
    POSITIONS = {
        'top': 1,
        'right': 1,
        'left': 0,
        'bottom': 0,
        'center': 0.5
    }
    
    def __init__(self, owner, x: float = 0, y: float = 0, width: float = 0, height: float = 0,
                 anchor_x: str = 'center', anchor_y: str = 'center', auto_move: bool = False):
        """
        Initialize the BoxModel with position, dimensions, and anchor points.
        
        Args:
            owner: The owner element that will be notified of movements.
            x: The initial x-coordinate position.
            y: The initial y-coordinate position.
            width: The width of the box.
            height: The height of the box.
            anchor_x: The horizontal anchor point ('left', 'center', 'right', or numeric).
            anchor_y: The vertical anchor point ('top', 'center', 'bottom', or numeric).
            auto_move: Whether to automatically notify owner on movement.
        """
        self.owner = owner
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._anchor_x = anchor_x
        self._anchor_y = anchor_y
        self._dx = 0.0
        self._dy = 0.0
        self.auto_move = auto_move
    
    def notify(self):
        """Notify the owner of accumulated movements and reset the deltas."""
        if self.owner:
            self.owner.move(self._dx, self._dy)
        self._dx = 0.0
        self._dy = 0.0
    
    def goto(self, x: float, y: float):
        """
        Move the box to absolute coordinates.
        
        Args:
            x: Target x-coordinate.
            y: Target y-coordinate.
        """
        self.move(x - self._x, y - self._y)
        
    def move(self, dx: float, dy: float):
        """
        Move the box by the specified deltas.
        
        Args:
            dx: Horizontal movement delta.
            dy: Vertical movement delta.
        """
        self._x += dx
        self._y += dy
        self._dx += dx
        self._dy += dy
        if self.auto_move:
            self.notify()
    
    def align(self, other: 'BoxModel', alignment: str):
        """
        Align another box relative to this one.
        
        Args:
            other: The other BoxModel to align.
            alignment: The alignment type ('top', 'bottom', 'left', 'right', 
                      'center_x', or 'center_y').
                      
        Raises:
            ValueError: If an invalid alignment is specified.
        """
        match alignment:
            case 'top':
                other.move(0, self.top - other.top)
            case 'bottom':
                other.move(0, self.bottom - other.bottom)
            case 'left':
                other.move(self.left - other.left, 0)
            case 'right':
                other.move(self.right - other.right, 0)
            case 'center_x':
                other.move(self.center_x - other.center_x, 0)
            case 'center_y':
                other.move(0, self.center_y - other.center_y)
            case _:
                raise ValueError(
                    f"Invalid alignment: {alignment}. Must be 'top', 'bottom', 'left', "
                    "'right', 'center_x', or 'center_y'"
                )
    
    def place_beside(self, other: 'BoxModel', side: str, indent: float = 0, 
                    align: str = 'center'):
        """
        Place another box beside this one with optional alignment.
        
        Args:
            other: The other BoxModel to place.
            side: The side to place on ('top', 'bottom', 'left', 'right').
            indent: The spacing between the boxes.
            align: The alignment type ('center', 'center_x', or 'center_y').
            
        Raises:
            ValueError: If an invalid side is specified.
        """
        new_x = new_y = 0.0
        match side:
            case 'top':
                new_y = self.top - other.bottom + indent
                if align == 'center':
                    align += '_x'
            case 'bottom':
                new_y = self.bottom - other.top - indent
                if align == 'center':
                    align += '_x'
            case 'left':
                new_x = self.left - other.right - indent
                if align == 'center':
                    align += '_y'
            case 'right':
                new_x = self.right - other.left + indent
                if align == 'center':
                    align += '_y'
            case _:
                raise ValueError(
                    f"Invalid side: {side}. Must be 'top', 'bottom', 'left', or 'right'"
                )

        other.move(new_x, new_y)    
        self.align(other, align)
    
    def place_inside(self, other: 'BoxModel', align_x: str = 'center', 
                    align_y: str = 'center'):
        """
        Place another box inside this one with specified alignments.
        
        Args:
            other: The BoxModel to place inside.
            align_x: Horizontal alignment ('center', 'center_x', 'left', 'right').
            align_y: Vertical alignment ('center', 'center_y', 'top', 'bottom').
        """
        if align_x == 'center':
            align_x += '_x'
        if align_y == 'center':
            align_y += '_y'
        self.align(other, align_x)
        self.align(other, align_y)
    
    @property
    def anchor_x(self) -> float:
        """Calculate the horizontal anchor offset."""
        if self._anchor_x in self.POSITIONS:
            return self._width * self.POSITIONS[self._anchor_x]
        return float(self._anchor_x)
    
    @property
    def anchor_y(self) -> float:
        """Calculate the vertical anchor offset."""
        if self._anchor_y in self.POSITIONS:
            return self._height * self.POSITIONS[self._anchor_y]
        return float(self._anchor_y)
    
    @property
    def top(self) -> float:
        """Get the top edge y-coordinate."""
        return self._y - self.anchor_y + self._height
    
    @property
    def bottom(self) -> float:
        """Get the bottom edge y-coordinate."""
        return self._y - self.anchor_y
    
    @property
    def right(self) -> float:
        """Get the right edge x-coordinate."""
        return self._x - self.anchor_x + self._width
    
    @property
    def left(self) -> float:
        """Get the left edge x-coordinate."""
        return self._x - self.anchor_x
    
    @property
    def center_x(self) -> float:
        """Get the center x-coordinate."""
        return self._x - self.anchor_x + self._width / 2
    
    @property
    def center_y(self) -> float:
        """Get the center y-coordinate."""
        return self._y - self.anchor_y + self._height / 2
    
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height
    
    def copy(self) -> 'BoxModel':
        """Create a copy of this BoxModel without an owner."""
        return BoxModel(
            owner=None,
            x=self._x,
            y=self._y,
            width=self._width,
            height=self._height,
            anchor_x=self._anchor_x,
            anchor_y=self._anchor_y
        )
    
    def dict(self):
        return dict(
            owner=self.owner,
            x=self._x,
            y=self._y,
            width=self._width,
            height=self._height,
            anchor_x=self._anchor_x,
            anchor_y=self._anchor_y
        )
        
class WrapBox(BoxModel):
    """
    A BoxModel that wraps another BoxModel with specified gaps (padding/margin).
    
    The gaps can be specified in CSS-style shorthand (1-4 values):
    - 1 value: uniform gap for all sides
    - 2 values: vertical and horizontal gaps
    - 3 values: top, horizontal, bottom
    - 4 values: top, right, bottom, left
    
    Attributes:
        owner: The BoxModel being wrapped.
        gaps: The gap values for each side (top, right, bottom, left).
    """
    
    def __init__(self, owner: BoxModel, gaps):
        """
        Initialize the WrapBox with an owner and gap values.
        
        Args:
            owner: The BoxModel to wrap.
            gaps: The gap values (1-4 values in CSS shorthand style).
            
        Raises:
            ValueError: If gaps has invalid number of values (not 1-4).
        """
        gap_count = len(gaps)
        if gap_count == 1:
            gaps = gaps * 4  
        elif gap_count == 2:
            gaps = gaps * 2  
        elif gap_count == 3:
            gaps = gaps + (gaps[1],)  
        elif gap_count != 4:
            raise ValueError('Gaps must have 1-4 values')
            
        super().__init__(auto_move=True, **(owner.dict()))
        self.owner = owner
        
        self._width += sum(gaps[1::2])
        self._height += sum(gaps[0::2])  

        self._x += owner.left - self.left - gaps[3]  
        self._y += owner.bottom - self.bottom - gaps[0]  


class PaddingBox(WrapBox):
    """
    A WrapBox that represents padding around an element.
    
    When placing elements inside, delegates to the owner's placement.
    """
    
    def place_inside(self, other: BoxModel, align_x: str = 'center', align_y: str = 'center'):
        """
        Place another box inside this padding box by delegating to the owner.
        
        Args:
            other: The BoxModel to place inside.
            align_x: Horizontal alignment ('center', 'left', 'right', etc.)
            align_y: Vertical alignment ('center', 'top', 'bottom', etc.)
        """
        self.owner.place_inside(other, align_x, align_y)


class MarginBox(PaddingBox):
    """
    A PaddingBox that represents margins around an element.
    
    Handles special margin collapsing behavior when placing boxes beside each other.
    """
    
    def place_beside(self, other: BoxModel, side: str, indent: float = 0, align: str = 'center'):
        """
        Place another box beside this one with margin collapsing behavior.
        
        When two MarginBoxes are placed adjacent, their margins collapse according to CSS rules.
        
        Args:
            other: The BoxModel to place beside.
            side: The side to place on ('top', 'bottom', 'left', 'right').
            indent: Additional spacing between the boxes.
            align: The alignment type ('center', 'center_x', 'center_y').
        """
        super().place_beside(other, side, indent, align)
        
        if isinstance(other, MarginBox):
            match side:
                case 'top':
                    self_margin = self.top - self.owner.top
                    other_margin = other.owner.bottom - other.bottom
                    adjustment = -(self_margin + other_margin) + max(self_margin, other_margin)
                    other.move(0, adjustment)
                    
                case 'bottom':
                    self_margin = self.owner.bottom - self.bottom
                    other_margin = other.top - other.owner.top
                    adjustment = +(self_margin + other_margin) - max(self_margin, other_margin)
                    other.move(0, adjustment)
                    
                case 'left':
                    self_margin = self.owner.left - self.left
                    other_margin = other.right - other.owner.right
                    adjustment = +(self_margin + other_margin) - max(self_margin, other_margin)
                    other.move(adjustment, 0)
                    
                case 'right':
                    self_margin = self.right - self.owner.right
                    other_margin = other.owner.left - other.left
                    adjustment = -(self_margin + other_margin) + max(self_margin, other_margin)
                    other.move(adjustment, 0)

class UIBox(MarginBox):
    """
    A composite box model representing a UI element with content, padding, and margin.
    
    This class combines multiple BoxModel layers to create a complete UI element:
    - Content box (innermost)
    - Padding box (wraps content)
    - Margin box (outermost, wraps padding)
    
    Attributes:
        content (BoxModel): The innermost content box representing the element's content area.
        padding (PaddingBox): The padding area around the content.
        margin (MarginBox): The margin area around the padding (inherits from MarginBox).
    """
    
    def __init__(self, owner, element, properties):
        """
        Initialize the UIBox with content, padding, and margin from element properties.
        
        Args:
            owner: The owner/parent element that will be notified of movements.
            element: The UI element containing the properties.
            properties: Dictionary of properties for the element.
        """
        # Initialize content box with parsed properties
        self.content = BoxModel(
            owner=owner,
            x=parse_expression(get_param('x', element, properties, 0), properties),
            y=parse_expression(get_param('y', element, properties, 0), properties),
            width=parse_expression(get_param('width', element, properties, 0), properties),
            height=parse_expression(get_param('height', element, properties, 0), properties),
            anchor_x=parse_expression(get_param('anchor_x', element, properties, 'center'), properties),
            anchor_y=parse_expression(get_param('anchor_y', element, properties, 'center'), properties),
            auto_move=True
        )
        
        # Create padding box around the content
        padding = parse_gap(element, properties, 'padding')
        self.padding = PaddingBox(self.content, padding)
        
        # Create margin box around the padding (super() calls MarginBox.__init__)
        margin = parse_gap(element, properties, 'margin')
        super().__init__(self.padding, margin)


