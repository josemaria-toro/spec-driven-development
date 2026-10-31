using System.Collections.Generic;

using Microsoft.AspNetCore.Http;

namespace App.Api;

/// <summary>The greeting endpoint: validates its input and answers with the greeting.</summary>
public static class GreetingEndpoint
{
    /// <summary>The longest accepted name.</summary>
    public const int MaxNameLength = 100;

    /// <summary>The route of the endpoint.</summary>
    public const string Route = "/greetings/{name}";

    /// <summary>Answers the greeting for a name, or a validation problem when the name is too long.</summary>
    /// <param name="name">The name from the route.</param>
    /// <param name="greeter">The greeting capability.</param>
    /// <returns>The result of the request.</returns>
    public static IResult Handle(string name, IGreeter greeter)
    {
        if (name.Length > MaxNameLength)
        {
            return Results.ValidationProblem(new Dictionary<string, string[]>
            {
                ["name"] = [$"The name must have at most {MaxNameLength} characters."],
            });
        }

        return Results.Ok(new GreetingResponse(greeter.Greet(name)));
    }
}
