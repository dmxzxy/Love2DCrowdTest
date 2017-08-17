﻿namespace Evaders.Spectator.OpenGL
{
    using System.Collections.Generic;
    using System.Linq;
    using Client;
    using Microsoft.Xna.Framework;
    using Microsoft.Xna.Framework.Graphics;
    using Microsoft.Xna.Framework.Input;

    public class ScreenGameRenderer : Screen
    {
        public override Color BackgroundColor => new Color(60, 0, 0);
        private const float MaxZoom = 2f, MinZoom = 0.2f;
        private static readonly Color[] PlayerColorArray = {Color.DarkRed, Color.CornflowerBlue, Color.Goldenrod, Color.White, Color.Purple, Color.Chocolate, Color.OrangeRed, Color.Honeydew};
        private readonly IGameProvider _games;
        private readonly Dictionary<long, int> _playerColorMapper = new Dictionary<long, int>();
        private Vector2 _cameraPosition = Vector2.Zero;
        private bool _firstUpdate;
        private long _gameViewIdentifier;
        private KeyboardState _lastKeyboardState;
        private MouseState _lastMouseState;
        private float _zoom = 0.2f;

        public ScreenGameRenderer(IScreenManager manager, IGameProvider games) : base(manager)
        {
            _games = games;
        }

        public override void Draw(SpriteBatch spritebatch, GraphicsDeviceManager graphicsDeviceManager)
        {
            if (!_games.RunningGames.Any())
                return;

            if (!_games.RunningGames.ContainsKey(_gameViewIdentifier))
                _gameViewIdentifier = _games.RunningGames.First().Key;
            var game = _games.RunningGames[_gameViewIdentifier];

            var viewMatrix = Matrix.CreateTranslation(_cameraPosition.X, _cameraPosition.Y, 0f)*Matrix.CreateScale(_zoom, _zoom, 1f)*Matrix.CreateTranslation(graphicsDeviceManager.PreferredBackBufferWidth/2f, graphicsDeviceManager.PreferredBackBufferHeight/2f, 0f);


            spritebatch.Begin(transformMatrix: viewMatrix, blendState: BlendState.AlphaBlend, samplerState: SamplerState.LinearClamp);
            DrawCircle(spritebatch, Vector2.Zero, game.CurrentArenaRadius, Color.White);

            foreach (var validEntity in game.ValidEntities)
            {
                if (!_playerColorMapper.ContainsKey(validEntity.PlayerIdentifier))
                    _playerColorMapper.Add(validEntity.PlayerIdentifier, _playerColorMapper.Count);
                var entityColor = PlayerColorArray[_playerColorMapper[validEntity.PlayerIdentifier]];
                var outlineColor = validEntity.CanShoot ? Color.Green : Color.Red;
                const float outlineFactor = 0.8f;

                DrawCircle(spritebatch, validEntity.Position, validEntity.HitboxSize, outlineColor);
                DrawCircle(spritebatch, validEntity.Position, validEntity.HitboxSize*outlineFactor, entityColor);
            }

            foreach (var projectile in game.ValidProjectiles)
            {
                if (!_playerColorMapper.ContainsKey(projectile.PlayerIdentifier))
                    _playerColorMapper.Add(projectile.PlayerIdentifier, _playerColorMapper.Count);
                var entityColor = PlayerColorArray[_playerColorMapper[projectile.PlayerIdentifier]];

                DrawCircle(spritebatch, projectile.Position, projectile.HitboxSize, entityColor);
                //spritebatch.Draw(TextureManager.Get(Texture.Circle), destinationRectangle: new Rectangle((int)projectile.Position.X, (int)projectile.Position.Y, projectile.HitboxSize * 2, projectile.HitboxSize * 2), color: entityColor, origin: new Vector2(projectile.HitboxSize, projectile.HitboxSize));
            }

            spritebatch.End();
        }

        private void DrawCircle(SpriteBatch spriteBatch, Core.Utility.Vector2 position, double radius, Color color)
        {
            spriteBatch.Draw(TextureManager.Get(Texture.Circle), new Rectangle((int) (position.X - radius), (int) (position.Y - radius), (int) (radius*2), (int) (radius*2)), color);
        }

        private void DrawCircle(SpriteBatch spriteBatch, Vector2 position, double radius, Color color)
        {
            DrawCircle(spriteBatch, new Core.Utility.Vector2(position.X, position.Y), radius, color);
        }

        public override void UpdateActive(double deltaT, GraphicsDeviceManager graphicsDeviceManager)
        {
            if (!_firstUpdate)
            {
                _lastKeyboardState = Keyboard.GetState();
                _lastMouseState = Mouse.GetState();
                _firstUpdate = true;
                return;
            }

            var mouseState = Mouse.GetState();
            var keyboardState = Keyboard.GetState();
            if (mouseState.ScrollWheelValue != _lastMouseState.ScrollWheelValue)
            {
                var scale = mouseState.ScrollWheelValue - _lastMouseState.ScrollWheelValue < 0 ? 0.95f : 1.05f;
                _zoom = MathHelper.Clamp(_zoom*scale, MinZoom, MaxZoom);
            }

            if (_lastMouseState.LeftButton == ButtonState.Pressed && mouseState.LeftButton == ButtonState.Pressed)
            {
                var zoomFac = 1f/_zoom;
                _cameraPosition += new Vector2((mouseState.X - _lastMouseState.X)*zoomFac, (mouseState.Y - _lastMouseState.Y)*zoomFac);
            }

            if (keyboardState.IsKeyUp(Keys.Space) && _lastKeyboardState.IsKeyDown(Keys.Space))
            {
                var index = _games.RunningGames.Keys.ToList().IndexOf(_gameViewIdentifier);
                if (index != -1)
                    _gameViewIdentifier = _games.RunningGames.Keys.ToArray()[++index%_games.RunningGames.Count];
            }

            _lastKeyboardState = keyboardState;
            _lastMouseState = mouseState;
        }
    }
}