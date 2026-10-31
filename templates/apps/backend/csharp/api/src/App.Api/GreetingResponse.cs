namespace App.Api;

/// <summary>The body of a successful greeting.</summary>
/// <param name="Message">The greeting.</param>
public sealed record GreetingResponse(string Message);
