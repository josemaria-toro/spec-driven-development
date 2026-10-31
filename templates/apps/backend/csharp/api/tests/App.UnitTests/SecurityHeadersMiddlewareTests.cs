using System;
using System.Collections.Generic;
using System.Threading.Tasks;

using App.Api;

using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Http.Features;

using Xunit;

namespace App.UnitTests;

public sealed class SecurityHeadersMiddlewareTests
{
    [Fact]
    public async Task InvokeAsync_WhenTheResponseStarts_SetsTheSecurityHeaders()
    {
        var feature = new RecordingResponseFeature();
        var context = new DefaultHttpContext();
        context.Features.Set<IHttpResponseFeature>(feature);
        var nextWasCalled = false;
        var middleware = new SecurityHeadersMiddleware(_ =>
        {
            nextWasCalled = true;
            return Task.CompletedTask;
        });

        await middleware.InvokeAsync(context);
        await feature.StartResponseAsync();

        Assert.True(nextWasCalled);
        Assert.Equal("nosniff", context.Response.Headers["X-Content-Type-Options"]);
        Assert.Equal("DENY", context.Response.Headers["X-Frame-Options"]);
        Assert.Equal("no-referrer", context.Response.Headers["Referrer-Policy"]);
        Assert.Equal("no-store", context.Response.Headers["Cache-Control"]);
        Assert.Contains("frame-ancestors 'none'", context.Response.Headers["Content-Security-Policy"].ToString());
    }

    private sealed class RecordingResponseFeature : HttpResponseFeature
    {
        private readonly List<(Func<object, Task> Callback, object State)> _callbacks = [];

        public override void OnStarting(Func<object, Task> callback, object state) =>
            _callbacks.Add((callback, state));

        public async Task StartResponseAsync()
        {
            foreach (var (callback, state) in _callbacks)
            {
                await callback(state);
            }
        }
    }
}
