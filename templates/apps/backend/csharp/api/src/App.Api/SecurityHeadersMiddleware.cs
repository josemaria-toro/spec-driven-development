using System.Threading.Tasks;

using Microsoft.AspNetCore.Http;

namespace App.Api;

/// <summary>Adds the security headers every response of the API carries.</summary>
/// <param name="next">The next middleware of the pipeline.</param>
public sealed class SecurityHeadersMiddleware(RequestDelegate next)
{
    /// <summary>Registers the headers for when the response starts and continues the pipeline.</summary>
    /// <param name="context">The current request context.</param>
    /// <returns>A task that completes when the pipeline has run.</returns>
    public Task InvokeAsync(HttpContext context)
    {
        // Set when the response starts so the exception handler, which clears the response, keeps them.
        context.Response.OnStarting(SetHeaders, context.Response);
        return next(context);
    }

    private static Task SetHeaders(object state)
    {
        var headers = ((HttpResponse)state).Headers;
        headers["Cache-Control"] = "no-store";
        headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'";
        headers["Referrer-Policy"] = "no-referrer";
        headers["X-Content-Type-Options"] = "nosniff";
        headers["X-Frame-Options"] = "DENY";
        return Task.CompletedTask;
    }
}
