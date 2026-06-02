from .._constants import TILE_SIZE, SCREEN_MIDPOINT
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._visualizer import Visualizer


class GhostRenderer:
    def __init__(self, visualizer: "Visualizer") -> None:
        self.vis = visualizer
        self.visual_positions: list[dict] = []
        self.lerp_speed: float = 0.15

    def reset_visual_positions(self) -> None:
        vis = self.vis
        self.visual_positions = []
        for g in vis.gameplay.ghosts_maps[vis.gameplay.map_idx]:
            gx = float(g.x * TILE_SIZE + 16 + TILE_SIZE // 2 + 1)
            gy = float(g.y * TILE_SIZE + 16 + TILE_SIZE // 2 + 1)
            self.visual_positions.append({"x": gx, "y": gy})

    def update_and_draw(
        self,
        ghosts_frames: list,
        scared_sprites: list,
        current_frame: int,
    ) -> None:
        vis = self.vis
        ghosts = vis.gameplay.ghosts_maps[vis.gameplay.map_idx]

        for i, g in enumerate(ghosts):
            target_gx = (
                (g.x * TILE_SIZE) + SCREEN_MIDPOINT[0]
                - vis.maze_size[0] // 2 + 14
            )
            target_gy = (
                (g.y * TILE_SIZE) + SCREEN_MIDPOINT[1]
                - vis.maze_size[1] // 2 + 15
            )

            self.visual_positions[i]["x"] += (
                target_gx - self.visual_positions[i]["x"]
            ) * self.lerp_speed
            self.visual_positions[i]["y"] += (
                target_gy - self.visual_positions[i]["y"]
            ) * self.lerp_speed

            angle = getattr(g, "ghost_angle", 0)

            if g.is_scared:
                dir_key = "0"
                ghost_dict = scared_sprites[0]
            else:
                dir_key = (
                    "W" if angle == 90
                    else "S" if angle == 270
                    else "A" if angle == 180
                    else "D"
                )
                ghost_dict = ghosts_frames[i % 2]

            if isinstance(ghost_dict, dict):
                dir_frames = ghost_dict[dir_key]
                frame = dir_frames[current_frame % len(dir_frames)]
                rect = frame.get_rect(
                    center=(
                        int(self.visual_positions[i]["x"]),
                        int(self.visual_positions[i]["y"]),
                    )
                )
                if not g.is_dead():
                    vis.screen.blit(frame, rect)
