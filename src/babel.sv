
function [15:0] rng_step;
    input [15:0] state;
    reg [15:0] s;
    begin
        s = state;
        s = s ^ (s << 5);
        s = s + 16'd62179;
        s = s ^ 16'd10208;
        s = s ^ (s << 7);
        rng_step = s;
    end
endfunction

module babel(
    input clk,
    input reset,
    input [4:0] charIn, //32 bit: [a-z][ .,!?;]
    input setSeed,
    output [4:0] charOut, //32 bit: [a-z][ .,!?;]
    output isWriting
);
    logic [7:0] counter;
    logic [15:0] state;
    logic [15:0] nextState;

    always_comb begin : randgen //16 bit random-esque function
        if(setSeed)begin
            nextState = {state[10:5]+1'b1, charIn, state[15:11]} ^ (state << 2);
        end else begin
            nextState = rng_step(state);
        end
    end

    logic pageGo;
    assign pageGo = (counter != 8'hFF);
    always @(posedge clk) begin : registers
        if(!reset)begin
            state <= 27143;
            counter <= 0;
        end else if(pageGo) begin
            state <= nextState;
            if(!setSeed) begin
                counter <= counter + 1;
            end
        end
    end

    assign isWriting = pageGo;
    assign charOut = pageGo ? state[15:11] : 0;

endmodule